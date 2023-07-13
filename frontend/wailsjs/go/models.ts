export namespace main {
	
	export class MyConfig {
	    pdf_path: string;
	    python_path: string;
	    tesseract_path: string;
	    pandoc_path: string;
	    hashcat_path: string;
	
	    static createFrom(source: any = {}) {
	        return new MyConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.pdf_path = source["pdf_path"];
	        this.python_path = source["python_path"];
	        this.tesseract_path = source["tesseract_path"];
	        this.pandoc_path = source["pandoc_path"];
	        this.hashcat_path = source["hashcat_path"];
	    }
	}

}

