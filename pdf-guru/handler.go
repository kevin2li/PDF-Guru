package main

import "github.com/gin-gonic/gin"
import "github.com/kevin2li/pdf-guru/pkg/pdftool"

func RotatePDF(c *gin.Context) {
	pdftool.RotatePDF()
}
