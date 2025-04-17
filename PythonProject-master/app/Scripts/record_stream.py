import asyncio
import os
import shutil
import subprocess
from pathlib import Path
import time
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

class StreamRecorder:
    def __init__(self, output_dir: str = None, max_workers: int = 4):
        # Use absolute path to the recordings directory
        base_dir = Path(__file__).parent.parent
        self.output_dir = (base_dir / "recordings") if output_dir is None else Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def _prepare_source_directory(self, source_id: int, source_name: str) -> Path:
        """Create directory for source recordings"""
        source_dir = self.output_dir / f"{source_id}"

        if source_dir.exists():
            try:
                shutil.rmtree(source_dir)  # Remove existing directory
            except Exception as e:
                logger.error(f"Failed to remove existing directory {source_dir}: {str(e)}")
                raise RuntimeError(f"Failed to remove existing directory {source_dir}: {str(e)}")
                
        source_dir.mkdir(parents=True, exist_ok=True)
        return source_dir

    async def _run_ffmpeg(self, cmd: List[str]) -> Tuple[bool, str]:
        """Run FFmpeg command in thread pool"""
        try:
            process = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            )
            return process.returncode == 0, process.stderr
        except Exception as e:
            logger.error(f"FFmpeg execution failed: {str(e)}")
            return False, str(e)

    async def record_stream(
        self, 
        stream_url: str, 
        source_name: str,
        stream_id: int,
        stream_name: str,
        duration: int = 15,
        output_dir: Path = None
    ) -> Dict:
        """Record a single stream with robust error handling"""
        if output_dir is None:
            output_dir = self.output_dir
            
        output_file = output_dir / f"{source_name}_{stream_id}.mp4"
        
        cmd = [
                "ffmpeg",
                "-y",
                
                "-timeout", "10000000",
                "-reconnect", "1",
                "-reconnect_at_eof", "1",
                "-reconnect_streamed", "1",
                "-reconnect_delay_max", "10",
                "-fflags", "+nobuffer",
                
                "-i", stream_url,
                
                "-t", str(duration),
                "-c", "copy",
                "-movflags", "+faststart",
                "-f", "mp4",
                str(output_file)
]
        
        success, error = await self._run_ffmpeg(cmd)
        
        return {
            "stream_id": stream_id,
            "output_file": str(output_file),
            "stream_name":stream_name,
            "success": success,
            "error": error,
            "url": stream_url
        }