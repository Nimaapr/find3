package models

/*
This code is part of a Go package models. It defines a structure called BinaryStats that calculates statistics for binary classification.
The structure has fields for true positives (TruePositives), false positives (FalsePositives), true negatives (TrueNegatives), and false negatives (FalseNegatives) counts, as well as the following metrics derived from these counts:

Sensitivity (Sensitivity) or True Positive Rate
Specificity (Specificity) or True Negative Rate
Informedness (Informedness) (Sensitivity + Specificity - 1)
Matthews Correlation Coefficient (MCC)
Fisher's P test (FisherP)

The function NewBinaryStats returns a BinaryStats object given the counts of true positives (tp), false positives (fp), true negatives (tn), and false negatives (fn). It calculates the statistics using the given counts and sets the fields of the returned BinaryStats object.

The function NChooseK calculates the number of combinations (n choose k) of n elements taken k at a time. The function first calculates this value using the Binomial function of the big package and then converts it to a float64 using the SetInt and Float64 functions of the big.Float type.
*/

import (
	"math"
	"math/big"
)

// BinaryStats is a structure that derives the following metrics https://en.wikipedia.org/wiki/Sensitivity_and_specificity
type BinaryStats struct {
	TruePositives  int `json:"true_positives"`
	FalsePositives int `json:"false_positives"`
	TrueNegatives  int `json:"true_negatives"`
	FalseNegatives int `json:"false_negatives"`

	// Sensitivity or true positive rate
	Sensitivity float64 `json:"sensitivity"`
	// Specificity or true negative rate
	Specificity float64 `json:"specificity"`
	// Informedness (TPR + SPC - 1)
	Informedness float64 `json:"informedness"`
	// Martthews Correlation coefficient
	MCC float64 `json:"mcc"`
	// Fisher's P test
	FisherP float64 `json:"fisher_p"`
}

// NewBinaryStats returns a binary stats object
func NewBinaryStats(tp, fp, tn, fn int) BinaryStats {
	tpf := float64(tp)
	fpf := float64(fp)
	tnf := float64(tn)
	fnf := float64(fn)
	sensitivity := float64(0)
	if tpf+fnf != 0 {
		sensitivity = tpf / (tpf + fnf)
	}
	specificity := float64(0)
	if tnf+fpf != 0 {
		specificity = tnf / (tnf + fpf)
	}
	mcc := float64(0)
	if math.Sqrt((tpf+fpf)*(tpf+fnf)*(tnf+fpf)*(tnf+fnf)) > 0 {
		mcc = (tpf*tnf - fpf*fnf) / math.Sqrt((tpf+fpf)*(tpf+fnf)*(tnf+fpf)*(tnf+fnf))
	}
	fisher_p := float64(1)
	if NChooseK(tpf+fpf+tnf+fnf, tpf+fpf) > 0 {
		fisher_p = NChooseK(tpf+fnf, tpf) * NChooseK(fpf+tnf, fpf) / NChooseK(tpf+fpf+tnf+fnf, tpf+fpf)
	}

	return BinaryStats{
		TruePositives:  tp,
		FalsePositives: fp,
		TrueNegatives:  tn,
		FalseNegatives: fn,

		Sensitivity:  sensitivity,
		Specificity:  specificity,
		Informedness: specificity + sensitivity - 1,
		MCC:          mcc,
		FisherP:      fisher_p,
	}
}

func NChooseK(n float64, k float64) float64 {
	a := big.NewInt(0)
	a.Binomial(int64(n), int64(k))
	f, _ := (new(big.Float).SetInt(a).Float64())
	return f
}
