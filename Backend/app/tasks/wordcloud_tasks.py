import logging
import os
from collections import Counter

from wordcloud import WordCloud as WC

from app.core.celery_app import celery
from app.db.session import SessionLocal
from app.models.pdf import PdfTopWordsStat
from app.models.wordcloud import WordcloudArtifact
from app.storage.paths import wordcloud_dir

logger = logging.getLogger(__name__)


@celery.task(name="app.tasks.wordcloud_tasks.generate_wordcloud")
def generate_wordcloud(artifact_id: str) -> None:
    db = SessionLocal()
    try:
        artifact = (
            db.query(WordcloudArtifact)
            .filter(WordcloudArtifact.id == artifact_id)
            .first()
        )
        if artifact is None:
            logger.error("Wordcloud artifact %s not found", artifact_id)
            return

        # Aggregate word frequencies across all associated PDFs
        frequencies: Counter[str] = Counter()
        for pdf in artifact.pdfs:
            stat = (
                db.query(PdfTopWordsStat)
                .filter(PdfTopWordsStat.pdf_id == pdf.id)
                .first()
            )
            if stat and isinstance(stat.words_json, list):
                for entry in stat.words_json:
                    if isinstance(entry, dict) and "word" in entry and "count" in entry:
                        frequencies[entry["word"]] += entry["count"]

        if not frequencies:
            logger.warning("No word data for wordcloud artifact %s", artifact_id)
            artifact.image_path = None
            db.commit()
            return

        wc = WC(width=800, height=400, background_color="white")
        wc.generate_from_frequencies(dict(frequencies))

        out_dir = wordcloud_dir(str(artifact.user_id))
        os.makedirs(out_dir, exist_ok=True)
        image_path = os.path.join(out_dir, f"{artifact_id}.png")
        wc.to_file(image_path)

        artifact.image_path = image_path
        db.commit()

    except Exception:
        logger.exception("generate_wordcloud task failed for %s", artifact_id)
    finally:
        db.close()
