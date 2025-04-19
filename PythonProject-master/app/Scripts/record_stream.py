import asyncio
import shutil
import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor
import signal

logger = logging.getLogger(__name__)

class StreamRecorder:
    def __init__(self, output_dir: str = None, max_workers: int = 120):
        # Maintain original initialization exactly
        base_dir = Path(__file__).parent.parent
        self.output_dir = (base_dir / "recordings") if output_dir is None else Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def _prepare_source_directory(self, source_id: int, source_name: str) -> Path:
        """Original directory preparation method with enhanced error handling"""
        source_dir = self.output_dir / f"{source_id}"
        try:
            # Non-blocking file operations
            await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: shutil.rmtree(source_dir, ignore_errors=True))
            await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: source_dir.mkdir(parents=True, exist_ok=True))
            return source_dir
        except Exception as e:
            logger.error(f"Directory error: {str(e)}")
            raise RuntimeError(f"Failed to prepare directory: {str(e)}")

    async def _run_ffmpeg(self, cmd: List[str]) -> Tuple[bool, str]:
        """Original method name with enhanced timeout handling"""
        try:
            # Add combined timeout system
            process = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    lambda: subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=25  # Process timeout
                    )
                ),
                timeout=30  # Total timeout including queue
            )
            return process.returncode == 0, process.stderr
        except asyncio.TimeoutError:
            logger.warning("FFmpeg timed out")
            return False, "Operation timed out"
        except Exception as e:
            logger.error(f"FFmpeg error: {str(e)}")
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
        """Your original method signature with optimized parameters"""
        output_dir = output_dir or self.output_dir
        output_file = output_dir / f"{source_name}_{stream_id}.mp4"
        
        # Enhanced FFmpeg command while maintaining your structure
        cmd = [
            "ffmpeg", "-y",
            "-timeout", "10000000",      # Increased from 3s to 10s
            "-reconnect", "1",          # Added reconnect attempts
            "-reconnect_delay_max", "5", # Max delay between attempts
            "-reconnect_streamed", "1",
            "-reconnect_on_network_error", "1",
            "-fflags", "+nobuffer+genpts",
            "-protocol_whitelist", "file,http,https,tcp,tls",
            "-rw_timeout", "15000000",   # Added I/O timeout
            "-i", stream_url,
            "-t", str(duration),
            "-c", "copy",
            "-movflags", "+faststart",
            "-loglevel", "error",
            str(output_file)
        ]
        
        success, error = await self._run_ffmpeg(cmd)
        
        # Add post-recording validation
        if success and output_file.exists():
            file_size = output_file.stat().st_size
            if file_size < 102400:  # 100KB minimum
                success = False
                error = f"File too small ({file_size} bytes)"
                output_file.unlink(missing_ok=True)
        
        return {
            "stream_id": stream_id,
            "output_file": str(output_file),
            "stream_name": stream_name,
            "success": success,
            "error": error,
            "url": stream_url
        }

    # Add graceful shutdown if missing in original
    def __del__(self):
        self.executor.shutdown(wait=False)