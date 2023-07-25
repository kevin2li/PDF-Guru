package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strconv"

	"github.com/pkg/errors"
)

func (a *App) CheckTrialCount() (int, error) {
	countPath := filepath.Join(logdir, "debug.log")
	count := 0
	if _, err := os.Stat(countPath); err == nil {
		// file exists
		countFile, err := os.OpenFile(countPath, os.O_RDONLY, 0666)
		if err != nil {
			err = errors.Wrap(err, "无法验证试用状态！")
			return count, err
		}
		defer countFile.Close()
		countBytes, err := os.ReadFile(countPath)
		if err != nil {
			err = errors.Wrap(err, "无法验证试用状态！")
			return count, err
		}
		count, err = strconv.Atoi(string(countBytes))
		if err != nil {
			err = errors.Wrap(err, "无法验证试用状态！")
			return count, err
		}
		countFile.Close()
		countFile, err = os.OpenFile(countPath, os.O_WRONLY|os.O_TRUNC, 0666)
		if err != nil {
			err = errors.Wrap(err, "无法验证试用状态！")
			return count, err
		}
		defer countFile.Close()
		countFile.WriteString(strconv.Itoa(count + 1))
		return count + 1, nil
	} else if os.IsNotExist(err) {
		// file not exists
		countFile, err := os.OpenFile(countPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
		if err != nil {
			err = errors.Wrap(err, "无法验证试用状态！")
			return count, err
		}
		defer countFile.Close()
		countFile.WriteString("1")
		return 1, nil
	}
	return count, fmt.Errorf("无法验证试用状态！")
}
