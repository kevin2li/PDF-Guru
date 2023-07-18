package main

import (
	"os"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"

	"github.com/pkg/errors"
)

func (a *App) CheckOS() string {
	return runtime.GOOS
}

func (a *App) CheckFileExists(path string) error {
	path = strings.TrimSpace(path)
	if path == "" {
		return errors.New("路径不能为空!")
	}
	if strings.Contains(path, "*") {
		matches, err := filepath.Glob(path)
		if err != nil {
			err = errors.Wrap(err, "")
			return err
		}
		if len(matches) == 0 {
			return errors.New("未匹配到任何文件")
		}
		return nil
	}
	if !filepath.IsAbs(path) {
		return errors.New("路径必须是绝对路径!")
	}
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return errors.New("路径不存在!")
	}
	if info, err := os.Stat(path); err == nil && info.IsDir() {
		return errors.New("路径是目录!")
	}
	return nil
}

func (a *App) CheckOutputDirExists(path string) error {
	if !filepath.IsAbs(path) {
		return errors.New("路径必须是绝对路径!")
	}
	if info, err := os.Stat(path); err == nil && !info.IsDir() {
		return errors.New("路径是文件，不是目录!")
	}
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return errors.New("路径不存在，继续则自动创建目录!")
	}
	return nil
}

func (a *App) CheckOutputFileExists(path string) error {
	if !filepath.IsAbs(path) {
		return errors.New("路径必须是绝对路径!")
	}
	if info, err := os.Stat(path); err == nil {
		if info.IsDir() {
			return errors.New("路径是目录，不是文件!")
		}
		return errors.New("路径已存在，继续则覆盖文件!")
	}
	return nil
}

func (a *App) CheckRangeFormat(pages string) error {
	pages = strings.TrimSpace(pages)
	parts := strings.Split(pages, ",")
	pos_count, neg_count := 0, 0
	for _, part := range parts {
		pattern := regexp.MustCompile(`^!?(\d+|N)(\-(\d+|N))?$`)
		part = strings.TrimSpace(part)
		if !pattern.MatchString(part) {
			return errors.New("页码格式错误!,示例：1-3,5,6-N")
		}
		if part[0] == '!' {
			neg_count++
		} else {
			pos_count++
		}
	}
	if pos_count > 0 && neg_count > 0 {
		return errors.New("不能同时使用正向选择和反向选择!")
	}
	return nil
}
