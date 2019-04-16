
function m423()
{
    for f in *.m4a; do ffmpeg -i "$f" -acodec libmp3lame -ab 64k "${f%}.mp3"; done
    for f in *.m4b; do ffmpeg -i "$f" -acodec libmp3lame -ab 64k "${f%}.mp3"; done
}


