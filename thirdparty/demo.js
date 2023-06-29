// var document = new Document("C:\\Users\\kevin\\Downloads\\mupdf-1.22.1-windows\\test.pdf");
// print(document); // [object pdf_document]
// var numPages = document.countPages();
// print(numPages);

function f(path) {
    var document = new Document(path);
    var numPages = document.countPages();
    print(numPages);

    // var outline = document.loadOutline();
    // print(outline.length);
    // for (var i = 0; i < outline.length; i++) {
    //     print(outline[i].title, outline[i].uri);
    // }

    var obj = document.outlineIterator();
    var result = obj.item();
    print(result.title, result.uri);
    while (result = obj.next()) {
        print(result.title, result.uri);
    }
    // var result = obj.item();
    // var result = outlineIterator.next();
    // print(result.title, result.uri);
}

f(scriptArgs)

