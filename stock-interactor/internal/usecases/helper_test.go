package usecases

import (
	"testing"

	"github.com/stretchr/testify/suite"
)

type decideSuite struct {
	suite.Suite
}

func TestDecideSuite(t *testing.T) {
	suite.Run(t, new(decideSuite))
}
