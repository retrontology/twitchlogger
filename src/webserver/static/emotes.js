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
    return a[1][0] - b[1][0];
}

function parse_twitch_emotes(emote_string, dark_mode = true) {

    if (emote_string == null || emote_string == 'None') {
        return [];
    } else {

        let color_mode = '';
        if (dark_mode) {
            color_mode = "dark";
        } else {
            color_mode = "light";
        }

        var emotes = emote_string.split('/');
        var emote_indexes = [];
        for (var emote in emotes) {
            emote = emotes[emote];
            console.log(emote);
            var [emote_id, occurances] = emote.split(':');
            console.log(occurances);
            var url = 'https://static-cdn.jtvnw.net/emoticons/v2/' + emote_id + '/default/' + color_mode + '/';
            var occurances = occurances.split(',');
            console.log(occurances)
            for (var occurance in occurances) {
                occurance = occurances[occurance];
                var [start, end] = occurance.split('-');
                var start = parseInt(start, 10);
                var end = parseInt(end, 10);
                emote_indexes.push([url, [start, end]])
            }
        }
        return emote_indexes;
    }
}

function replace_emotes(message, emote_indexes) {
    emote_indexes.sort(compare_indexes);
    var snippets = [];
    var last_end = 0;
    for (var emote_index in emote_indexes) {

        emote_index = emote_indexes[emote_index];
        console.log(emote_index)
        let url = emote_index[0];
        let start = emote_index[1][0];
        let end = emote_index[1][1]+1;

        let content_fragment = `<span class='content-fragment'>${message.slice(last_end, start)}</span>`
        snippets.push(content_fragment);

        let emote_text = message.slice(start, end);
        let snippet = `<img alt="${emote_text}" src="${url}1.0" srcset="${url}1.0 1x,${url}2.0 2x,${url}3.0 4x"></img>`;
        console.log('Snippet: ' + snippet);
        snippets.push(snippet);
        last_end = end;
    }
    if (last_end < message.length) {
        let content_fragment = `<span class='content-fragment'>${message.slice(last_end)}</span>`;
        snippets.push(content_fragment);
    }
    var output = '';
    for (var snippet in snippets) {
        output += snippets[snippet];
    }
    return output;
}

async function parse_table() {
    let table = document.getElementById('messages');

    ffz_global = await fetch_ffz_global_emotes();
    bttv_global = await fetch_bttv_global_emotes();
    seventv_global = await fetch_7tv_global_emotes();

    for (let i in table.rows) {
        let row = table.rows[i];
        for (let j in row.cells) {
            let cell = row.cells[j]
            if (cell.classList != undefined && cell.classList.contains("message-content")) {
                let twitch_emotes = cell.getAttribute('data-emotes');
                twitch_emotes =  parse_twitch_emotes(twitch_emotes)

                cell.innerHTML = replace_emotes(cell.innerHTML, twitch_emotes);
            }
        }
    }
}

async function parse_emotes(table) {

    

    ffz_channels = {};
    bttv_channels = {};
    seventv_channels = {};

    for (let i in table.rows) {
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