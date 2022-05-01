async function fetch_ffz_channel_emotes(channel) {
    channel = channel.toLowerCase()
    let url = 'https://api.frankerfacez.com/v1/room/' + channel
    let response = await fetch('/readme.txt');
    if (response.status === 200) {
        const data = await response.json();
        var emotes = []
        for (var emote_set in data.sets) {
            for (var emote of data.sets[emote_set].emoticons) {

            }
        }
        return emotes;
    }
}

async function fetch_bttv_global_emotes() {
    url = 'https://api.betterttv.net/3/cached/emotes/global'
}

