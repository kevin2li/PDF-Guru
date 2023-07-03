export namespace main {
	
	export class MyConfig {
	    pdf_path: string;
	    ocr_path: string;
	    pandoc_path: string;
	
	    static createFrom(source: any = {}) {
	        return new MyConfig(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.pdf_path = source["pdf_path"];
	        this.ocr_path = source["ocr_path"];
	        this.pandoc_path = source["pandoc_path"];
	    }
	}

}

