extends Node
## Grading (autoload)
## Fictional grading company. Computes a grade from a card's condition.
## Economy (fee, PL deduction) is applied by Game.grade_card.

func grader_name() -> String:
	return Balance.GRADER_NAME

func fee() -> float:
	return Balance.GRADING_FEE

## Roll a 1..10 grade biased by the raw condition. 10 is rare.
func roll_grade(condition: int) -> int:
	var mean: float = Balance.CONDITION_GRADE_MEAN.get(condition, 6.0)
	var g := roundi(RNGService.randfn(mean, Balance.GRADE_NOISE))
	return clampi(g, 1, 10)
