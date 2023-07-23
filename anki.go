package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"

	"github.com/pkg/errors"
)

type DeckNames struct {
	Names   []string `json:"data"`
	Status  string   `json:"status"`
	Message string   `json:"message"`
}

func (a *App) GetDeckNames() ([]string, error) {
	args := []string{"anki", "--type", "deck_names", "placeholder"}
	logger.Println(args)
	config, err := a.LoadConfig()
	if err != nil {
		err = errors.Wrap(err, "")
		return nil, err
	}
	cmd := exec.Command(config.PdfPath, args...)
	out, err := cmd.CombinedOutput()
	if err != nil {
		err = errors.Wrap(err, "命令执行失败!"+string(out))
		logger.Errorln("Error:", err)
		return nil, err
	}
	logger.Println(string(out))
	ret_path := filepath.Join(logdir, "cmd_output.json")
	var ret DeckNames
	data, err := os.ReadFile(ret_path)
	if err != nil {
		err = errors.Wrap(err, "read cmd output file error")
		return nil, err
	}
	err = json.Unmarshal(data, &ret)
	if err != nil {
		err = errors.Wrap(err, "json umarshal error")
		return nil, err
	}

	if ret.Status != "success" {
		logger.Errorf("Error: %v\n", ret.Message)
		return nil, errors.New(ret.Message)
	}
	return ret.Names, nil
}

func (a *App) CreateCardByRectAnnots(
	inFile string,
	outFile string,
	address string,
	parentDeck string,
	mode []string,
	createSubDeck bool,
	level int,
	q_mask_color string,
	a_mask_color string,
	dpi int,
	tags []string,
	imageMode bool,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, address: %s, parentDeck: %s, mode: %v, createSubDeck: %v, level: %d, q_mask_color: %s, a_mask_color: %s, dpi: %d, tags: %v, pages: %s\n", inFile, outFile, address, parentDeck, mode, createSubDeck, level, q_mask_color, a_mask_color, dpi, tags, pages)
	args := []string{"anki"}
	args = append(args, "--type", "rect_annots")
	args = append(args, "--address", address)
	args = append(args, "--parent-deck", parentDeck)
	args = append(args, "--mode")
	args = append(args, mode...)
	if createSubDeck {
		args = append(args, "--create-sub-deck")
	}
	args = append(args, "--level", fmt.Sprintf("%d", level))
	args = append(args, "--q-mask-color", q_mask_color)
	args = append(args, "--a-mask-color", a_mask_color)
	args = append(args, "--dpi", fmt.Sprintf("%d", dpi))
	if len(tags) > 0 {
		args = append(args, "--tags")
		args = append(args, tags...)
	}
	if imageMode {
		args = append(args, "--image-mode")
	}
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}

func (a *App) CreateCardByFontStyle(
	inFile string,
	outFile string,
	matches []string,
	pages string) error {
	logger.Printf("inFile: %s, outFile: %s, matches: %v, pages: %s\n", inFile, outFile, matches, pages)
	args := []string{"anki"}
	args = append(args, "--type", "font_style")
	args = append(args, "--matches")
	args = append(args, matches...)
	if pages != "" {
		args = append(args, "--page_range", pages)
	}
	if outFile != "" {
		args = append(args, "-o", outFile)
	}
	args = append(args, inFile)
	logger.Println(args)
	return a.cmdRunner(args, "pdf")
}
