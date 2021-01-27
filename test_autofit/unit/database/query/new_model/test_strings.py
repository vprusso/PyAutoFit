from autofit.database import query_model as q


class TestString:
    def test_named_query(self):
        query = q.Q(
            "a"
        )

        assert query.query == (
            "SELECT parent_id "
            "FROM object AS o "
            "WHERE o.name = 'a'"
        )

    def test_with_string(self):
        query = q.Q(
            "a",
            q.SV(
                "=",
                'value'
            )
        )

        assert query.query == (
            "SELECT parent_id "
            "FROM object AS o, "
            "string_value AS sv "
            "WHERE o.name = 'a' "
            "AND sv.value = 'value'"
        )

    def test_with_value(self):
        query = q.Q(
            "a",
            q.V(
                "=",
                1
            )
        )

        assert query.query == (
            "SELECT parent_id "
            "FROM object AS o, "
            "value AS v "
            "WHERE o.name = 'a' "
            "AND v.value = 1"
        )

    def test_simple_and(
            self,
            simple_and
    ):
        assert simple_and.query == (
            "SELECT parent_id "
            "FROM object AS o, "
            "value AS v "
            "WHERE o.name = 'a' "
            "AND v.value < 1 "
            "AND v.value > 0"
        )

    def test_simple_or(
            self,
            simple_or
    ):
        assert simple_or.query == (
            "SELECT parent_id "
            "FROM object AS o, "
            "value AS v "
            "WHERE o.name = 'a' "
            "AND v.value < 1 "
            "OR v.value > 0"
        )

    def test_second_level(
            self,
            second_level
    ):
        assert second_level.query == (
            "SELECT parent_id "
            "FROM object AS o, "
            "value AS v "
            "WHERE id IN ("
            "SELECT parent_id "
            "FROM object AS o, "
            "value AS v "
            "WHERE o.name = 'b' "
            "AND v.value > 0"
            ") "
            "AND o.name = 'a' "
            "AND v.value < 1"
        )
