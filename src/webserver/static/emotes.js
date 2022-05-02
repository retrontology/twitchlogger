async function fetch_ffz_emotes(url) {
    let response = await fetch(url);
    if (response.status === 200) {
        const data = await response.json();
        var emotes = [];
        for (var emote_set in data.sets) {
            emotes = emotes.concat(data.sets[emote_set].emoticons);
        }
        return emotes;
    }
    else {
        return [];
    }
}

async function fetch_ffz_channel_emotes(channel_id) {
    let url = 'https://api.frankerfacez.com/v1/room/id/' + channel_id
    const emotes = await fetch_ffz_emotes(url);
    return emotes;
}

async function fetch_ffz_global_emotes() {
    let url = 'https://api.frankerfacez.com/v1/set/global'
    const emotes = await fetch_ffz_emotes(url);
    return emotes;
}

function parse_ffz_emotes(message, emotes) {

}

async function fetch_bttv_channel_emotes(channel_id) {
    let url = 'https://api.betterttv.net/3/cached/users/twitch/' + channel_id;
    if (response.status === 200) {
        const data = await response.json();
        const emotes = data.channelEmotes.concat(data.sharedEmotes);
        return emotes;
    }
    else {
        return [];
    }
}

async function fetch_bttv_global_emotes() {
    let url = 'https://api.betterttv.net/3/cached/emotes/global';
    if (response.status === 200) {
        const emotes = await response.json();
        return emotes;
    }
    else {
        return [];
    }
}

async function fetch_7tv_global_emotes() {
    let url = 'https://api.7tv.app/v2/emotes/global'
    if (response.status === 200) {
        const emotes = await response.json();
        return emotes;
    }
    else {
        return [];
    }
}

async function fetch_7tv_channel_emotes(channel) {
    let url = 'https://api.7tv.app/v2/users/' + channel + '/emotes'
    if (response.status === 200) {
        const emotes = await response.json();
        return emotes;
    }
    else {
        return [];
    }
}

function compare_indexes(a, b) {
    return a[1][0]-b[1][0];
}

async function parse_twitch_emotes(message, emote_string, dark_mode=true) {

    if (emote_string == "") {
        return message;
    }

    if (dark_mode) {
        const mode = "dark";
    } else {
        const mode = "light";
    }

    const emotes = emote_string.split('/');
    var emote_indexes = [];
    for (var emote in emotes) {
        var [emote_id, occurances] = emote.split(':');
        var url = 'https://static-cdn.jtvnw.net/emoticons/v2/' + emote_id + '/static/' + mode + '/';
        var occurances = occurances.split(',');
        for (var occurance in occurances) {
            var [start, end] = occurance.split('-');
            var start = parseInt(start, 10);
            var end = parseInt(end, 10);
            emote_indexes.push([url, [start, end]])
        }
    }
    emote_indexes.sort(compare_indexes);
    var snippets = [];
    var last_end = 0;
    for (var emote_index in emote_indexes) {
        let url = emote_index[0];
        let start = emote_index[1][0];
        let end = emote_index[1][0];
        let length = end - start;
        snippets.push(message.splice(last_end, start));
        let emote_text = message.splice(start, end);

        let snippet = '<img alt="';
        snippet += emote_text;
        snippet += '" src="';
        snippet += url;
        snippet += '1.0" srcset="';
        snippet += url; 
        snippet += '1.0 1x,';
        snippet += url;
        snippet += '2.0 2x,';
        snippet += url;
        snippet += '3.0 4x"></img>';
        snippets.push(snippet);

        last_end = end;
    }
}

async function parse_emotes() {

    ffz_global = await fetch_ffz_global_emotes();
    bttv_global = await fetch_bttv_global_emotes();
    seventv_global = await fetch_7tv_global_emotes();

    ffz_channels = {};
    bttv_channels = {};
    seventv_channels = {};

    for (let i in this.rows) {
        let row = table.rows[i];
        let channel_id = row.getAttribute('data-channel-id');
        let channel = row.getAttribute('data-channel');
        if (!(channel in ffz_channels)) {
            ffz_channels[channel] = fetch_ffz_channel_emotes(channel_id);
        }
        if (!(channel in bttv_channels)) {
            ffz_channels[channel] = fetch_bttv_channel_emotes(channel_id);
        }
        if (!(channel in seventv_channels)) {
            seventv_channels[channel] = fetch_ffz_channel_emotes(channel_id);
        }
        let message = ''
        for (let j in row.cells) {
            let cell = row.cells[j]
            if (cell.classList.contains("message-content")) {
                let message = cell.innerText
                
                break;
            }
        }
    }
}