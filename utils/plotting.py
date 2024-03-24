import altair as alt


def select_nearest():
    return alt.selection(
        type="single",
        nearest=True,
        on="mouseover",
        fields=["x"],
        empty="none",
        clear="mouseout",
    )


def get_selectors(df, selection, x="x:Q"):
    return (
        alt.Chart(df)
        .mark_point()
        .encode(x=x, opacity=alt.value(0))
        .add_selection(selection)
    )


def add_text(chart, field, selection):
    return (
        chart.mark_text(align="right", dx=-5, dy=-12, color="white", fontSize=18)
        .encode(text=field)
        .transform_filter(selection)
    )


def mark_years(df, x="x:Q"):
    return (
        alt.Chart(df)
        .mark_rule(color="white")
        .encode(x=x, strokeDash=alt.value([5, 5]), strokeWidth=alt.value(2))
        .transform_filter(alt.datum.x % 365 == 0)
    )


def add_rules(df, selection, color="gray", x="x:Q"):
    return alt.Chart(df).mark_rule(color=color).encode(x=x).transform_filter(selection)
