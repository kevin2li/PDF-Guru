package main

import "fmt"

func (a *App) AddPDFHeaderAndFooter(
	inFile string,
	outFile string,
	header_left string,
	header_center string,
	header_right string,
	footer_left string,
	footer_center string,
	footer_right string,
	margin_bbox []float32,
	unit string,
	font_family string,
	font_size int,
	font_color string,
	opacity float32,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, header_left: %s, header_center: %s, header_right: %s, footer_left: %s, footer_center: %s, footer_right: %s, margin_bbox: %v, unit: %s, font_family: %s, font_size: %d, font_color: %s, opacity: %f, pages: %s\n", inFile, outFile, header_left, header_center, header_right, footer_left, footer_center, footer_right, margin_bbox, unit, font_family, font_size, font_color, opacity, pages)
	args := []string{"header_footer", "--type", "add"}
	if header_left != "" {
		args = append(args, "--header-left", header_left)
	}
	if header_center != "" {
		args = append(args, "--header-center", header_center)
	}
	if header_right != "" {
		args = append(args, "--header-right", header_right)
	}
	if footer_left != "" {
		args = append(args, "--footer-left", footer_left)
	}
	if footer_center != "" {
		args = append(args, "--footer-center", footer_center)
	}
	if footer_right != "" {
		args = append(args, "--footer-right", footer_right)
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
	return a.cmdRunner(args, "pdf")
}

func (a *App) RemovePDFHeaderAndFooter(
	inFile string,
	outFile string,
	margin_bbox []float32,
	remove_list []string,
	unit string,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, margin_bbox: %v, remove_list: %v, unit: %s, pages: %s\n", inFile, outFile, margin_bbox, remove_list, unit, pages)
	args := []string{"header_footer", "--type", "remove"}
	if len(margin_bbox) > 0 {
		args = append(args, "--margin-bbox")
		for _, v := range margin_bbox {
			args = append(args, fmt.Sprintf("%f", v))
		}
	}
	if len(remove_list) > 0 {
		args = append(args, "--remove")
		args = append(args, remove_list...)
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
	return a.cmdRunner(args, "pdf")
}
