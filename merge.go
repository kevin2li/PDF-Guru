package main

import "github.com/pkg/errors"

func (a *App) MergePDF(inFiles []string, outFile string, sortMethod string, sortDirection string) error {
	if len(inFiles) == 0 {
		return errors.New("no input files")
	}
	args := []string{"merge"}
	if sortMethod != "" {
		args = append(args, "--sort_method", sortMethod)
	}
	if sortDirection != "" {
		args = append(args, "--sort_direction", sortDirection)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFiles...)
	logger.Println(args)

	return a.cmdRunner(args, "pdf")
}
