import math

import pytest

import autofit as af
from test_autofit.mock import MockClassGaussian, MockClassInf, EllipticalSersic


class TestPriorLimits:
    def test_out_of_order_prior_limits(self):
        with pytest.raises(af.exc.PriorException):
            af.UniformPrior(1.0, 0)
        with pytest.raises(af.exc.PriorException):
            af.GaussianPrior(0, 1, 1, 0)

    def test_in_or_out(self):
        prior = af.GaussianPrior(0, 1, 0, 1)
        with pytest.raises(af.exc.PriorLimitException):
            prior.assert_within_limits(-1)

        with pytest.raises(af.exc.PriorLimitException):
            prior.assert_within_limits(1.1)

        prior.assert_within_limits(0.0)
        prior.assert_within_limits(0.5)
        prior.assert_within_limits(1.0)

    def test_no_limits(self):
        prior = af.GaussianPrior(0, 1)

        prior.assert_within_limits(100)
        prior.assert_within_limits(-100)
        prior.assert_within_limits(0)
        prior.assert_within_limits(0.5)

    def test_uniform_prior(self):
        prior = af.UniformPrior(0, 1)

        with pytest.raises(af.exc.PriorLimitException):
            prior.assert_within_limits(-1)

        with pytest.raises(af.exc.PriorLimitException):
            prior.assert_within_limits(1.1)

        prior.assert_within_limits(0.0)
        prior.assert_within_limits(0.5)
        prior.assert_within_limits(1.0)

    def test_prior_creation(self):
        mm = af.ModelMapper()
        mm.mock_class_gaussian = MockClassGaussian

        prior_tuples = mm.prior_tuples_ordered_by_id

        assert prior_tuples[0].prior.lower_limit == 0
        assert prior_tuples[0].prior.upper_limit == 1

        assert prior_tuples[1].prior.lower_limit == 0
        assert prior_tuples[1].prior.upper_limit == 2

    def test_out_of_limits(self):
        mm = af.ModelMapper()
        mm.mock_class_gaussian = MockClassGaussian

        assert mm.instance_from_vector([1, 2]) is not None

        with pytest.raises(af.exc.PriorLimitException):
            mm.instance_from_vector(([1, 3]))

        with pytest.raises(af.exc.PriorLimitException):
            mm.instance_from_vector(([-1, 2]))

    def test_inf(self):
        mm = af.ModelMapper()
        mm.mock_class_inf = MockClassInf

        prior_tuples = mm.prior_tuples_ordered_by_id

        assert prior_tuples[0].prior.lower_limit == -math.inf
        assert prior_tuples[0].prior.upper_limit == 0

        assert prior_tuples[1].prior.lower_limit == 0
        assert prior_tuples[1].prior.upper_limit == math.inf

        assert mm.instance_from_vector([-10000, 10000]) is not None

        with pytest.raises(af.exc.PriorLimitException):
            mm.instance_from_vector(([1, 0]))

        with pytest.raises(af.exc.PriorLimitException):
            mm.instance_from_vector(([0, -1]))

    def test_preserve_limits_tuples(self):
        mm = af.ModelMapper()
        mm.mock_class_gaussian = MockClassGaussian

        new_mapper = mm.mapper_from_gaussian_tuples([(0.0, 0.5), (0.0, 1)])

        prior_tuples = new_mapper.prior_tuples_ordered_by_id

        assert prior_tuples[0].prior.lower_limit == 0
        assert prior_tuples[0].prior.upper_limit == 1

        assert prior_tuples[1].prior.lower_limit == 0
        assert prior_tuples[1].prior.upper_limit == 2

    def test_from_gaussian_no_limits(self):
        mm = af.ModelMapper()
        mm.mock_class_gaussian = MockClassGaussian

        new_mapper = mm.mapper_from_gaussian_tuples(
            [(0.0, 0.5), (0.0, 1)],
            no_limits=True
        )

        priors = new_mapper.priors
        assert priors[0].lower_limit == float("-inf")
        assert priors[0].upper_limit == float("inf")
        assert priors[1].lower_limit == float("-inf")
        assert priors[1].upper_limit == float("inf")


class TestPriorMean:
    def test_simple(self):
        uniform_prior = af.UniformPrior(0.0, 1.0)
        assert uniform_prior.mean == 0.5

        uniform_prior.mean = 1.0
        assert uniform_prior.lower_limit == 0.5
        assert uniform_prior.upper_limit == 1.5

    def test_higher(self):
        uniform_prior = af.UniformPrior(1.0, 2.0)
        assert uniform_prior.mean == 1.5

        uniform_prior.mean = 2.0
        assert uniform_prior.lower_limit == 1.5
        assert uniform_prior.upper_limit == 2.5


class TestAddition:
    def test_abstract_plus_abstract(self):
        one = af.AbstractModel()
        two = af.AbstractModel()
        one.a = "a"
        two.b = "b"

        three = one + two

        assert three.a == "a"
        assert three.b == "b"

    def test_list_properties(self):
        one = af.AbstractModel()
        two = af.AbstractModel()
        one.a = ["a"]
        two.a = ["b"]

        three = one + two

        assert three.a == ["a", "b"]

    def test_instance_plus_instance(self):
        one = af.ModelInstance()
        two = af.ModelInstance()
        one.a = "a"
        two.b = "b"

        three = one + two

        assert three.a == "a"
        assert three.b == "b"

    def test_mapper_plus_mapper(self):
        one = af.ModelMapper()
        two = af.ModelMapper()
        one.a = af.PriorModel(EllipticalSersic)
        two.b = af.PriorModel(EllipticalSersic)

        three = one + two

        assert three.prior_count == 14


class TestUniformPrior:
    def test__simple_assumptions(self):
        uniform_simple = af.UniformPrior(lower_limit=0.0, upper_limit=1.0)

        assert uniform_simple.value_for(0.0) == 0.0
        assert uniform_simple.value_for(1.0) == 1.0
        assert uniform_simple.value_for(0.5) == 0.5

    def test__non_zero_lower_limit(self):
        uniform_half = af.UniformPrior(lower_limit=0.5, upper_limit=1.0)

        assert uniform_half.value_for(0.0) == 0.5
        assert uniform_half.value_for(1.0) == 1.0
        assert uniform_half.value_for(0.5) == 0.75

    def test_width(self):
        assert af.UniformPrior(2, 5).width == 3

    def test_negative_range(self):
        prior = af.UniformPrior(-1, 0)
        assert prior.width == 1
        assert prior.value_for(0.0) == -1
        assert prior.value_for(1.0) == 0.0


class TestLogUniformPrior:
    def test__simple_assumptions(self):
        log_uniform_simple = af.LogUniformPrior(lower_limit=1.0e-8, upper_limit=1.0)

        assert log_uniform_simple.value_for(0.0) == 1.0e-8
        assert log_uniform_simple.value_for(1.0) == 1.0
        assert log_uniform_simple.value_for(0.5) == 0.0001

    def test__non_zero_lower_limit(self):
        log_uniform_half = af.LogUniformPrior(lower_limit=0.5, upper_limit=1.0)

        assert log_uniform_half.value_for(0.0) == 0.5
        assert log_uniform_half.value_for(1.0) == 1.0
        assert log_uniform_half.value_for(0.5) == pytest.approx(0.70710678118, 1.0e-4)


class TestGaussianPrior:
    def test__simple_assumptions(self):
        gaussian_simple = af.GaussianPrior(mean=0.0, sigma=1.0)

        assert gaussian_simple.value_for(0.1) == pytest.approx(-1.281551, 1.0e-4)
        assert gaussian_simple.value_for(0.9) == pytest.approx(1.281551, 1.0e-4)
        assert gaussian_simple.value_for(0.5) == 0.0

    def test__non_zero_mean(self):
        gaussian_half = af.GaussianPrior(mean=0.5, sigma=2.0)

        assert gaussian_half.value_for(0.1) == pytest.approx(-2.0631031, 1.0e-4)
        assert gaussian_half.value_for(0.9) == pytest.approx(3.0631031, 1.0e-4)
        assert gaussian_half.value_for(0.5) == 0.5