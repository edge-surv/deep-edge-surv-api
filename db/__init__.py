from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()


supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")


supabase: Client = create_client(supabase_url, supabase_key)


async def upload_file_to_storage(file_path: str, bucket: str = "videos") -> str:
    """Upload file to Supabase storage and return public URL"""
    with open(file_path, "rb") as f:
        file_name = os.path.basename(file_path)
        supabase.storage.from_(bucket).upload(file_name, f)
        return supabase.storage.from_(bucket).get_public_url(file_name)


async def upload_frame_to_storage(
    frame_data: bytes, frame_name: str, bucket: str = "frames"
) -> str:
    """Upload frame data to Supabase storage and return public URL"""
    supabase.storage.from_(bucket).upload(frame_name, frame_data)
    return supabase.storage.from_(bucket).get_public_url(frame_name)
