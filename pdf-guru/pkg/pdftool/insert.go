package backend

import "fmt"

func InsertPDF(inFile1 string, inFile2 string, insertPos int, dstPages string, posType string, outFile string) error {
	logger.Printf("inFile1: %s, inFile2: %s, insertPos: %d, dstPages: %s, posType: %s, outFile: %s\n", inFile1, inFile2, insertPos, dstPages, posType, outFile)
	args := []string{"insert"}
	if insertPos != 0 {
		args = append(args, "--insert_pos", fmt.Sprintf("%d", insertPos))
	}
	if posType != "" {
		args = append(args, "--pos-type", posType)
	}
	if dstPages != "" {
		args = append(args, "--page_range", dstPages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile1)
	args = append(args, inFile2)
	logger.Println(args)

	return cmdRunner(args, "pdf")
}

func InsertBlankPDF(inFile string, outFile string, insertPos int, posType string, paper_size string, orientation string, count int) error {
	logger.Printf("inFile: %s, outFile: %s, insertPos: %d, posType: %s, paper_size: %s, orientation: %s, count: %d\n", inFile, outFile, insertPos, posType, paper_size, orientation, count)
	args := []string{"insert", "--method", "blank"}
	args = append(args, "--insert_pos", fmt.Sprintf("%d", insertPos))
	if posType != "" {
		args = append(args, "--pos-type", posType)
	}
	if paper_size != "" {
		args = append(args, "--paper_size", paper_size)
	}
	if orientation != "" {
		args = append(args, "--orientation", orientation)
	}
	args = append(args, "--count", fmt.Sprintf("%d", count))
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile, "placeholder.pdf")
	logger.Println(args)

	return cmdRunner(args, "pdf")
}

func ReplacePDF(inFile1 string, inFile2 string, srcPages string, dstPages string, outFile string) error {
	logger.Printf("inFile1: %s, inFile2: %s, srcPages: %s, dstPages: %s, outFile: %s\n", inFile1, inFile2, srcPages, dstPages, outFile)
	args := []string{"replace"}
	if srcPages != "" {
		args = append(args, "--src_page_range", srcPages)
	}
	if dstPages != "" {
		args = append(args, "--dst_page_range", dstPages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile1)
	args = append(args, inFile2)
	logger.Println(args)

	return cmdRunner(args, "pdf")
}
