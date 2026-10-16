from src.genai4simpy_agent.tools import make_run_python


def test_run_python_executes_with_project_interpreter(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SECRET_API_KEY", "x")
    rp = make_run_python(timeout=60, work_dir="wf")
    out = rp.invoke({"code": "import os, pandas; print('ok', os.getcwd().endswith('wf'), 'SECRET_API_KEY' in os.environ)"})
    assert out.strip() == "ok True False", out


def test_spec_store_parallel_writes(tmp_path, monkeypatch):
    import json
    from concurrent.futures import ThreadPoolExecutor
    from src.genai4simpy_agent.spec import SpecStore
    monkeypatch.chdir(tmp_path)
    st = SpecStore("rep")
    secs = ["assumptions"] * 20 + ["resources"] * 20
    def put(i_sec):
        i, sec = i_sec
        st.put(sec, [f"a{i}"] if sec == "assumptions" else [{"name": f"r{i}", "resource_class": "r"}], "t")
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(put, enumerate(secs)))
    spec = json.load(open(st.path))
    assert {"assumptions", "resources"} <= set(spec)
