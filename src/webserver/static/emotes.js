const Provider = {
    Twitch: 'Twitch',
    FFZ: 'FFZ',
    BTTV: 'BTTV',
    SevenTV: 'SevenTV'
}
const PROVIDER_ORDER = [
    Provider.Twitch,
    Provider.FFZ,
    Provider.BTTV,
    Provider.SevenTV
]

function compare_indexes(a, b) {
    var result = a[1][0] - b[1][0];
    if (result == 0){
        return PROVIDER_ORDER.indexOf(a[2]) - PROVIDER_ORDER.indexOf(b[2]);
    } else{
        return result;
    }
}

function parse_twitch_emotes(emote_string, dark_mode = true) {
    let color_mode = '';
    if (dark_mode) {
        color_mode = "dark";
    } else {
        color_mode = "light";
    }
    let url = 'https://static-cdn.jtvnw.net/emoticons/v2/%i/default/' + color_mode + '/%s.0';
    return parse_emotes(emote_string, url, Provider.Twitch);
}

function parse_ffz_emotes(emote_string) {
    let url = 'https://cdn.frankerfacez.com/emote/%i/%s';
    return parse_emotes(emote_string, url, Provider.FFZ);
}

function parse_bttv_emotes(emote_string) {
    let url = 'https://cdn.betterttv.net/emote/%i/%sx';
    return parse_emotes(emote_string, url, Provider.BTTV);
}

function parse_seventv_emotes(emote_string) {
    let url = 'https://cdn.7tv.app/emote/%i/%sx';
    return parse_emotes(emote_string, url, Provider.SevenTV);
}

function parse_emotes(emote_string, cdn_url, provider){

    if (emote_string == null || emote_string == 'None') {
        return [];
    } else {
        var emotes = emote_string.split('/');
        var emote_indexes = [];
        for (var emote in emotes) {
            emote = emotes[emote];
            var [emote_id, occurances] = emote.split(':');
            var url = cdn_url.replace('%i', emote_id);
            var occurances = occurances.split(',');
            for (var occurance in occurances) {
                occurance = occurances[occurance];
                var [start, end] = occurance.split('-');
                var start = parseInt(start, 10);
                var end = parseInt(end, 10);
                emote_indexes.push([url, [start, end], provider])
            }
        }
        return emote_indexes;
    }
}

function replace_emotes(cell, emote_indexes) {
    if (emote_indexes.length > 0) {
        emote_indexes.sort(compare_indexes);
        let last_end = 0;
        let index = 0;
        for (var emote_index of emote_indexes) {
            if (emote_index[1][0] >= last_end) {
                
                let url = emote_index[0];
                let start = emote_index[1][0] - last_end;
                let end = emote_index[1][1] + 1 - last_end;

                let start_fragment = cell.childNodes[index];
                let message = start_fragment.innerText;

                start_fragment.innerText = message.slice(0, start);

                let img_element = document.createElement('img');
                img_element.classList.add('content-emote');
                img_element.src = url.replace('%s', '1');
                img_element.srcset = `${url.replace('%s', '1')} 1x,${url.replace('%s', '2')} 2x,${url.replace('%s', '3')} 4x`;
                img_element.alt = message.slice(start, end);
                img_element.title = img_element.alt
                cell.appendChild(img_element);

                let next_fragment = document.createElement('span');
                next_fragment.classList.add('content-fragment');
                next_fragment.innerText = message.slice(end);
                cell.appendChild(next_fragment);

                last_end += end;
                index += 2;
            }
        }
    }
}

function parse_usernames(cell, channel) {
    let index = 0;
    while (index < cell.childNodes.length) {
        let child = cell.childNodes[index];
        if (child.tagName == 'SPAN') {
            let message = child.innerText;
            let match = /@([A-Z,a-z,0-9])\w+/.exec(message);
            if (match) {
                child.innerText = message.slice(0, match.index);

                let username = message.slice(match.index + 1, match.index + match[0].length).toLowerCase();

                let user_link = document.createElement('a');
                user_link.innerText = message.slice(match.index, match.index + match[0].length);
                user_link.classList.add('message-user-mention');
                user_link.href = `/channel/${channel}?username=${username}`;

                child.insertAdjacentElement('afterend', user_link);

                let next_fragment = document.createElement('span');
                next_fragment.classList.add('content-fragment');
                next_fragment.innerText = message.slice(match.index + match[0].length);

                user_link.insertAdjacentElement('afterend', next_fragment);


            }
        }
        index += 1;
    }
}

async function parse_table() {
    let table = document.getElementById('messages');
    for (let i in table.rows) {
        if (i == 0 || table.rows[i].getAttribute == undefined) {
            continue;
        }
        let row = table.rows[i];

        let channel = row.getAttribute('data-channel');
        let channel_id = row.getAttribute('data-channel-id');

        for (let j in row.cells) {
            let cell = row.cells[j]
            
            if (cell.classList != undefined && cell.classList.contains("message-content")) {

                let twitch_emotes = cell.getAttribute('data-emotes');
                twitch_emotes = parse_twitch_emotes(twitch_emotes);

                let ffz_emotes = cell.getAttribute('data-emotes-ffz');
                ffz_emotes = parse_ffz_emotes(ffz_emotes);

                let bttv_emotes = cell.getAttribute('data-emotes-bttv');
                bttv_emotes = parse_bttv_emotes(bttv_emotes);

                let seventv_emotes = cell.getAttribute('data-emotes-seventv');
                seventv_emotes = parse_seventv_emotes(seventv_emotes);

                replace_emotes(cell, twitch_emotes.concat(ffz_emotes, bttv_emotes, seventv_emotes));
                parse_usernames(cell, channel);

            }
        }
    }
}