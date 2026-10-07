"""Verificações numéricas e de execução dos 31 laboratórios didáticos."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from experiments import (
    EXPERIMENTS, attention, bpe_train, chunks, cosine, dpo_loss,
    evaluate_cases, group_advantages, layer_norm, lexical_scores,
    retrieval_metrics, rope, rrf, sampling_distribution, softmax,
    validate_tool_call, wilson_interval,
)


def test_softmax_stable_and_normalized():
    np.testing.assert_allclose(softmax([10000, 10001]), softmax([0, 1]))
    np.testing.assert_allclose(softmax([[1, 2], [3, 4]]).sum(axis=1), 1)
    with pytest.raises(ValueError):
        softmax([1, 2], 0)


def test_causal_attention_blocks_future_contributions():
    q = np.array([[1, 0], [0, 1], [1, 1]])
    v = np.array([[1, 2], [3, 4], [5, 6]])
    scores, weights, output = attention(q, q, v, causal=True)
    assert np.isneginf(scores[0, 1])
    assert weights[0, 1] == weights[0, 2] == weights[1, 2] == 0
    np.testing.assert_allclose(output[0], v[0])
    changed = v.copy()
    changed[-1] = 100000
    np.testing.assert_allclose(attention(q, q, changed, causal=True)[2][:2], output[:2])
    np.testing.assert_allclose(weights.sum(axis=1), 1)


def test_bpe_merges_non_overlapping_pairs_and_preserves_characters():
    words, history = bpe_train("aaaa aaaa", 1)
    assert history[0]["par"] == "a + a"
    assert words == [["aa", "aa", "▁"], ["aa", "aa", "▁"]]
    assert bpe_train("", 10) == ([], [])
    final, _ = bpe_train("baixo baixa baixo", 20)
    assert ["".join(w) for w in final] == ["baixo▁", "baixa▁", "baixo▁"]


def test_sampling_keeps_crossing_token_and_renormalizes():
    logits = np.log([.5, .3, .2])
    result = sampling_distribution(logits, 1, 3, .6)
    np.testing.assert_allclose(result, [.625, .375, 0])
    np.testing.assert_allclose(sampling_distribution(logits, 1, 1, 1), [1, 0, 0])
    np.testing.assert_allclose(sampling_distribution(logits, 1, 3, 1), [.5, .3, .2])


def test_rope_preserves_norm_and_relative_position():
    x, y = np.array([1., 2, 3, 4]), np.array([2., -1, 3, -2])
    assert np.linalg.norm(rope(x, 7)) == pytest.approx(np.linalg.norm(x))
    assert rope(x, 3) @ rope(y, 8) == pytest.approx(rope(x, 0) @ rope(y, 5))
    np.testing.assert_allclose(layer_norm(x), layer_norm(x + 100))
    assert layer_norm(x).mean() == pytest.approx(0)
    assert cosine([1, 2], [2, 4]) == pytest.approx(1)


def test_alignment_losses_and_group_advantages():
    assert dpo_loss(1, 1, .2) == pytest.approx(math.log(2))
    assert dpo_loss(2, 1, .2) < dpo_loss(1, 1, .2)
    assert math.isfinite(dpo_loss(-10000, 10000, 1))
    np.testing.assert_allclose(group_advantages([1, 1, 1]), 0)
    assert group_advantages([0, 1, 2]).mean() == pytest.approx(0)


def test_retrieval_and_chunking():
    assert chunks(list("abcdefg"), 4, 1) == [list("abcd"), list("defg")]
    with pytest.raises(ValueError):
        chunks(list("abc"), 2, 2)
    fused = rrf([["a", "b"], ["b", "a"]], 60)
    assert dict(fused)["a"] == pytest.approx(dict(fused)["b"])
    result = retrieval_metrics(["x", "a", "b"], {"a", "b"}, 2)
    assert result["Recall@k"] == result["Precision@k"] == result["RR@k"] == .5
    assert retrieval_metrics(["a", "b"], {"a", "b"}, 2)["nDCG@k"] == pytest.approx(1)
    scores = lexical_scores("decoder causal", {"a": "decoder causal", "b": "base congelada"})
    assert scores["a"] == pytest.approx(1)
    assert scores["b"] == 0


@pytest.mark.parametrize("payload", [
    {"name": "eval", "arguments": {"a": 1, "b": 2}},
    {"name": "somar", "arguments": {"a": True, "b": 2}},
    {"name": "somar", "arguments": {"a": float("nan"), "b": 2}},
    {"name": "somar", "arguments": {"a": 10**1000, "b": 2}},
    {"name": "somar", "arguments": {"a": "1", "b": 2}},
    {"name": "somar", "arguments": {"a": 1, "b": 2, "extra": 3}},
    {"name": "somar", "arguments": {"a": 1, "b": 2}, "extra": 1},
    [],
])
def test_tool_contract_rejects_invalid_inputs(payload):
    assert validate_tool_call(payload)[0] is False


def test_tool_contract_and_evaluation():
    assert validate_tool_call({"name": "somar", "arguments": {"a": 12, "b": 30}}) == (True, 42)
    small = wilson_interval(8, 10)
    large = wilson_interval(800, 1000)
    assert small[0] < .8 < small[1]
    assert large[1] - large[0] < small[1] - small[0]
    assert wilson_interval(0, 100)[0] == 0
    cases = [{"esperado": "Lisboa", "resposta": " LISBOA  "}]
    assert bool(evaluate_cases(cases, True).iloc[0]["acerto"])
    assert not bool(evaluate_cases(cases, False).iloc[0]["acerto"])


@pytest.mark.parametrize("lesson", range(31))
def test_every_lesson_renders(lesson):
    from streamlit.testing.v1 import AppTest
    assert len(EXPERIMENTS) == 31
    app = AppTest.from_string(
        f"from experiments import render_experiment\nrender_experiment({lesson})"
    ).run(timeout=30)
    assert not app.exception, f"Aula {lesson}: {app.exception}"
    assert app.subheader


def test_mini_gpt_short_input_and_empty_rag_index():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_string("from experiments import render_experiment\nrender_experiment(9)").run()
    app.text_input[0].set_value("ab").run()
    assert not app.exception
    app = AppTest.from_string("from experiments import render_experiment\nrender_experiment(18)").run()
    app.multiselect[0].set_value(["D1", "D2", "D3", "D4", "D5", "D6"]).run()
    assert not app.exception
    assert app.warning


def test_retry_scenario_and_stateful_agent():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_string("from experiments import render_experiment\nrender_experiment(22)").run()
    app.button[0].click().run()
    assert not app.exception
    assert app.dataframe[0].value.iloc[-1]["Gravações"] == 1
    app.toggle[2].set_value(False).run()
    app.button[0].click().run()
    assert app.dataframe[0].value.iloc[-1]["Gravações"] == 2
    agent = AppTest.from_string("from experiments import render_experiment\nrender_experiment(23)").run()
    for _ in range(5):
        agent.button[0].click().run()
    assert not agent.exception
    assert agent.button[0].disabled
    assert "42" in agent.success[0].value
