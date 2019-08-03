
function m423()
{
    for f in *.m4a; do ffmpeg -i "$f" -acodec libmp3lame -ab 64k "${f%}.mp3"; done
    for f in *.m4b; do ffmpeg -i "$f" -acodec libmp3lame -ab 64k "${f%}.mp3"; done
}


function flac2mp3()
{
    find . -name "*.flac" -exec sh -c 'ffmpeg -i "$1" -ar 44100 -ac 2 -b:a 320k "${1%.flac}.mp3"' sh {} \;
}

function remove_quotes()
{
    temp="${1%\"}"
    temp="${temp#\"}"
    RES="${temp%.*}"
    return $RES
}


function duration()
{
    RES=$(ffprobe -show_streams -print_format json "$1"  -v fatal | jq '.streams[0].duration')
    temp="${RES%\"}"
    temp="${temp#\"}"
    RES="${temp%.*}"
    echo "$RES"
    return $RES
}

function duration_all_files()
{
    FILES=$1
    total=0
    for f in $FILES
    do
        res=$(duration "$f")
        total=$(($total+$res))
    done
    echo "$total"
    return $total
}

function remove_track_numbers()
{
    for f in *
    do
        echo "--- processing $f"
        rename 's/^[0-9]+[\s\.\-]+//' "$f"
    done
}


function yt-dla()
{
    youtube-dl --get-duration $1
    youtube-dl --extract-audio  --audio-format mp3 --audio-quality 1 $1
}

function yt-dlv()
{
    youtube-dl --get-duration $1
    youtube-dl --recode-video avi $1
}

function yta()
{
    youtube-dl -x --audio-format mp3 --audio-quality 1 --exec 'mv {} ~/pCloudDrive/__NEW/_YTA'  $@ &
}

function ytv()
{
    youtube-dl --exec 'mv {} ~/pCloudDrive/__NEW/_YTV'  $@ &
}

function nonums()
{
     rename -e 's/^[\d\.\s\-]+//' $1
}

function add_prefix()
{
     prefix=$1
     mask=$2
     rename -nono -e 's/^/$prefix/' $mask
}