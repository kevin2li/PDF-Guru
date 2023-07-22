package backend

import "fmt"

func AddPDFPageNumber(
	inFile string,
	outFile string,
	pos string,
	start int,
	format string,
	margin_bbox []float32,
	unit string,
	align string,
	font_family string,
	font_size int,
	font_color string,
	opacity float32,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, pos: %s, start: %d, format: %s, margin_bbox: %v, unit: %s, font_family: %s, font_size: %d, font_color: %s, opacity: %f, pages: %s\n", inFile, outFile, pos, start, format, margin_bbox, unit, font_family, font_size, font_color, opacity, pages)
	args := []string{"page_number", "--type", "add"}
	if pos != "" {
		args = append(args, "--pos", pos)
	}
	if start != 0 {
		args = append(args, "--start", fmt.Sprintf("%d", start))
	}
	if format != "" {
		args = append(args, "--format", format)
	}
	if align != "" {
		args = append(args, "--align", align)
	}
	if len(margin_bbox) > 0 {
		args = append(args, "--margin-bbox")
		for _, v := range margin_bbox {
			args = append(args, fmt.Sprintf("%f", v))
		}
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if font_family != "" {
		args = append(args, "--font-family", font_family)
	}
	if font_size != 0 {
		args = append(args, "--font-size", fmt.Sprintf("%d", font_size))
	}
	if font_color != "" {
		args = append(args, "--font-color", font_color)
	}
	if opacity != 0 {
		args = append(args, "--opacity", fmt.Sprintf("%f", opacity))
	}
	if pages != "" {
		args = append(args, "--page-range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)

	logger.Println(args)
	return cmdRunner(args, "pdf")
}

func RemovePDFPageNumber(
	inFile string,
	outFile string,
	margin_bbox []float32,
	pos string,
	unit string,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, margin_bbox: %v, pos: %s, unit: %s, pages: %s\n", inFile, outFile, margin_bbox, pos, unit, pages)
	args := []string{"page_number", "--type", "remove"}
	if len(margin_bbox) > 0 {
		args = append(args, "--margin-bbox")
		for _, v := range margin_bbox {
			args = append(args, fmt.Sprintf("%f", v))
		}
	}
	if pos != "" {
		args = append(args, "--pos", pos)
	}
	if unit != "" {
		args = append(args, "--unit", unit)
	}
	if pages != "" {
		args = append(args, "--page-range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)

	logger.Println(args)
	return cmdRunner(args, "pdf")
}
