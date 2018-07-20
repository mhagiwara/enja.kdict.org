var HASH_SIZE = 512;
var NUM_RESULTS = 15;
var dict = [];
var search_result = {};
var trigrams_to_merge;


function string2hash(str) {  // receives a string and returns a hash value for it
    // from http://werxltd.com/wp/2010/05/13/javascript-implementation-of-javas-string-hashcode-method/
    var hash = 0;
    var i;
    var char;

    if (str.length === 0) return hash;
    for (i = 0; i < str.length; i++) {
        char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
}

function loadDict(hash, onload) {
    if (hash in dict) {
        onload();
    }

    var script = document.createElement('script');
    script.onload = onload;
    script.src = 'data/' + ('00' + hash).slice(-3) + '.js';
    document.head.appendChild(script);
}

function ngrams(word, n) {
    var i;
    var result = [];
    for (i = 0; i < word.length - n + 1; i ++) {
        result.push(word.slice(i, i + n))
    }
    return result;
}

function word2vec(word) {
    var vec = {};
    var bigrams = ngrams(word, 2);
    var trigrams = ngrams(word, 3);
    var _len = 0;
    bigrams.forEach(function (bigram) {
        vec[bigram] = (vec[bigram] || 0) + 1;
        _len ++;
    });
    trigrams.forEach(function (trigram) {
        vec[trigram] = (vec[trigram] || 0) + 1;
        _len ++;
    });

    vec._len = _len;
    return vec;
}

function similarity(vec1, vec2) {
    var vec_long, vec_short;
    var overlap = 0;

    if (vec1._len >= vec2._len) {
        vec_long = vec1;
        vec_short = vec2;
    } else {
        vec_long = vec2;
        vec_short = vec1;
    }

    Object.getOwnPropertyNames(vec_short).forEach(function (key) {
        if (key === '_len') return;
        overlap += Math.min(vec_short[key], vec_long[key] || 0);
    });

    return 2. * overlap / (vec1._len + vec2._len);
}

function updateSearchResult(subdict, query_vec) {
    subdict.forEach(function (entry) {
        if (search_result.hasOwnProperty(entry.title)) return;

        var word_vec = word2vec('^' + entry.title + '$');
        var sim = similarity(word_vec, query_vec);
        search_result[entry.title] = entry;
        entry.sim = sim;
    });
}

function showSearchResult() {
    var results_to_show = [];
    var comparator = function (a, b) {
        return b.sim - a.sim;
    };
    var i, result;
    var ul, li;


    Object.getOwnPropertyNames(search_result).forEach(function (word) {
        if (search_result[word].sim > 0.2) {
            results_to_show.push(search_result[word])
        }
    });

    results_to_show.sort(comparator);

    ul = document.getElementById('results');
    while (ul.firstChild) {
        ul.removeChild(ul.firstChild);
    }

    for (i = 0; i < results_to_show.length && i < NUM_RESULTS; i ++) {
        li = document.createElement('li');
        result = results_to_show[i];
        li.innerHTML = '<b class="title">' + result.title + '</b> '
            + '<span class="def">' + result.definition + '</span>';
        ul.appendChild(li);
    }
}

function search(query) {
    var query_vec = word2vec('^' + query + '$');
    var trigrams = ngrams('^' + query + '$', 3);

    search_result = {};
    trigrams_to_merge = trigrams.length;

    trigrams.forEach(function (trigram) {
        var hash = string2hash(trigram) % HASH_SIZE;
        loadDict(hash, function () {
            updateSearchResult(dict[hash], query_vec);
            trigrams_to_merge --;
            if (trigrams_to_merge === 0) {
                showSearchResult();
            }
        });
    });
}

window.onload = function() {
    var query = document.getElementById('query');
    query.addEventListener('input', function () {
        search(this.value);
    });
};
