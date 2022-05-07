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

function parse_ffz_emotes(cell, global_emotes, channel_emotes) {

    let emotes = [];
    for (var set in global_emotes['sets']) {
        emotes = emotes.concat(global_emotes['sets'][set]['emoticons']);
    }
    for (var set in channel_emotes['sets']) {
        emotes = emotes.concat(channel_emotes['sets'][set]['emoticons']);
    }
    
    for (var emote of emotes) {
        let regexp = new RegExp('\\b' + emote['name'] + '\\b');
        let index = 0;
        while (index < cell.childNodes.length) {
            if (node.classList.contains("content-fragment")) {
                var match = regexp.exec(node.innerHTML);
                if (match) {
                    message = node.innerHTML;
                    node.innerHTML = node.innerHTML.slice(0, match.index);
                    var emote_image = document.createElement('img');
                    emote_image.src = 'https:' + emote['urls']['1'];
                    emote_image.setAttribute('alt', emote['name']);
                    if (emote['urls'].length > 1) {
                        var srcset_strings = [];
                        for (var url in emote['urls']) {
                            var size_string = 'https:' + emote['urls'][url] + ' ' + url + 'x';
                            srcset_strings.push(size_string);
                        }
                        emote_image.setAttribute('srcset', srcset_strings.join());
                    }
                    var rest_of_text = document.createElement('span');
                    rest_of_text.classList.add('content-fragment')
                    if (index >= cell.childNodes.length - 1) {
                        cell.appendChild(emote_image);
                        cell.appendChild(rest_of_text);
                    } else {
                        cell.insertBefore(emote_image, cell.childNodes[index+1]);
                        cell.insertBefore(emote_image, cell.childNodes[index+2]);
                    }
                    index += 1
                }
            }
            index += 1;
        }
    }
}

async function fetch_bttv_channel_emotes(channel_id) {
    let url = 'https://api.betterttv.net/3/cached/users/twitch/' + channel_id;
    let response = await fetch(url);
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
    let response = await fetch(url);
    if (response.status === 200) {
        const emotes = await response.json();
        return emotes;
    }
    else {
        return [];
    }
}

function parse_bttv_emotes(cell, global_emotes, channel_emotes) {
    let emotes = [...global_emotes];
    emotes = emotes.concat(channel_emotes['channelEmotes']);
    emotes = emotes.concat(channel_emotes['sharedEmotes']);
    
    for (var emote of emotes) {
        let regexp = new RegExp('\\b' + emote['code'] + '\\b');
        let index = 0;
        while (index < cell.childNodes.length) {
            node = cell.childNodes[index];
            if (node.classList.contains("content-fragment")) {
                var match = regexp.exec(node.innerHTML);
                if (match) {
                    message = node.innerHTML;
                    node.innerHTML = node.innerHTML.slice(0, match.index);
                    var url = 'https://cdn.betterttv.net/emote/' + emote['id'] + '/';
                    var emote_image = document.createElement('img');
                    emote_image.src = url + '1x';
                    emote_image.setAttribute('alt', emote['code']);
                    
                    var srcset = `${url}1.0 1x,${url}2.0 2x,${url}3.0 4x`;

                    emote_image.setAttribute('srcset', srcset);
                    
                    var rest_of_text = document.createElement('span');
                    rest_of_text.classList.add('content-fragment');
                    rest_of_text.innerHTML = message.slice(match.index);
                    if (index >= cell.childNodes.length - 1) {
                        cell.appendChild(emote_image);
                        cell.appendChild(rest_of_text);
                    } else {
                        cell.insertBefore(emote_image, cell.childNodes[index+1]);
                        cell.insertBefore(emote_image, cell.childNodes[index+2]);
                    }
                    index += 1
                }
            }
            index += 1;
        }
    }
}

async function fetch_7tv_global_emotes() {
    let url = 'https://api.7tv.app/v2/emotes/global'
    let response = await fetch(url);
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
    let response = await fetch(url);
    if (response.status === 200) {
        const emotes = await response.json();
        return emotes;
    }
    else {
        return [];
    }
}

function parse_7tv_emotes(message, emotes) {
    return [];
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
            var [emote_id, occurances] = emote.split(':');
            var url = 'https://static-cdn.jtvnw.net/emoticons/v2/' + emote_id + '/default/' + color_mode + '/';
            var occurances = occurances.split(',');
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
        let end = emote_index[1][1] + 1;

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

    ffz_channels = {};
    bttv_channels = {};
    seventv_channels = {};

    for (let i in table.rows) {
        if (i == 0) {
            continue;
        }
        let row = table.rows[i];

        let channel = row.getAttribute("data-channel");
        let channel_id = row.getAttribute("data-channel-id");

        if (!(channel in ffz_channels)) {
            ffz_channels[channel] = fetch_ffz_channel_emotes(channel_id);
        }
        if (!(channel in bttv_channels)) {
            bttv_channels[channel] = fetch_bttv_channel_emotes(channel_id);
        }
        if (!(channel in seventv_channels)) {
            seventv_channels[channel] = fetch_7tv_channel_emotes(channel);
        }

        for (let j in row.cells) {
            let cell = row.cells[j]
            if (cell.classList != undefined && cell.classList.contains("message-content")) {

                let twitch_emotes = cell.getAttribute('data-emotes');
                twitch_emotes = parse_twitch_emotes(twitch_emotes);
                cell.innerHTML = replace_emotes(cell.innerHTML, twitch_emotes);

                //parse_7tv_emotes(cell, seventv_global, seventv_channels[channel]);
                parse_bttv_emotes(cell, bttv_global, bttv_channels[channel]);
                //parse_ffz_emotes(cell, ffz_global, ffz_channels[channel]);
                
            }
        }
    }
}