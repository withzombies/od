(() => {
    const addScript = (uri, onload) => {
        const elt = document.createElement('script');
        elt.onload = onload;
        elt.setAttribute('src', uri);
        document.body.appendChild(elt);
    };

    const pad = (n, width, z) => {
        z = z || '0';
        n = n + '';
        return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
    }

    // load it & kick it off:
    window.module = {};
    addScript('https://cdn.jsdelivr.net/npm/streamsaver@2.0.4/StreamSaver.min.js', () => {
        const streamSaver = window.module.exports;
        window.module = undefined;
        console.log("loaded the streamsaver script", streamSaver);
        const savePath = (url, name) => {
            const fileStream = streamSaver.createWriteStream(name);
            fetch(url).then(res => {
                const readableStream = res.body;
                return readableStream.pipeTo(fileStream)
                    .then(() => console.log('done writing', url, "to", name));
            });
        };

        const saveFile = (contents, name) => {
            const blob = new Blob([JSON.stringify(contents)]);
            const outfile = streamSaver.createWriteStream(name)
            const readableStream = blob.stream();
            readableStream.pipeTo(outfile).then(() =>
                console.log("wrote manifest.json")
            )
        };

        const spines = window.bData.spine;
        for (let i = 0; i < spines.length; i++) {
            const spine = spines[i];
            const name = decodeURI(spine.path.split('?')[0])
            savePath(spine.path, `${name}`)
        }

        var manifest = {
            'title': window.bData.title.main,
            'author': window.bData.creator[0].name,
            'description': window.bData.description.full,
            chapters: []
        };
        const chapters = window.bData.nav.toc;
        for (let i = 0; i < chapters.length; i++) {
            manifest.chapters.push({ 'filename': `${pad(i, 2)}_${chapters[i].title}.mp3`, 'chapter': i, 'title': chapters[i].title, 'path': chapters[i].path })
        }
        saveFile(manifest, "manifest.json");

    });
})()
