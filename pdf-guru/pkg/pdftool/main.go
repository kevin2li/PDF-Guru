package backend

import (
	"io"
	"os"
	"path/filepath"
	"runtime"

	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
)

var (
	log    *logrus.Logger
	logger *logrus.Entry
	logdir string
	// tmpDir string
)

func init() {
	// init logger
	log = logrus.New()
	if runtime.GOOS == "windows" {
		logdir = filepath.Join(os.Getenv("USERPROFILE"), ".pdf_guru")
	} else {
		logdir = filepath.Join(os.Getenv("HOME"), ".pdf_guru")
	}
	err := os.MkdirAll(logdir, 0755)
	if err != nil {
		err = errors.Wrap(err, "failed to create log directory")
		log.Fatal(err)
	}
	logpath := filepath.Join(logdir, "access.log")
	file, err := os.OpenFile(logpath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		err = errors.Wrap(err, "failed to create log file")
		log.Fatal(err)
	}
	defer file.Close()

	log.SetOutput(io.MultiWriter(os.Stdout, file))
	log.SetLevel(logrus.DebugLevel)
	log.SetReportCaller(true)
	log.SetFormatter(&logrus.TextFormatter{
		TimestampFormat: "2006-01-02 15:04:05",
		FullTimestamp:   true,
		DisableColors:   true,
	})
	logger = log.WithFields(logrus.Fields{
		"service": "pdf-guru",
	})
	logger.Info("starting pdf-guru")

}
