# Contributing

Add one file per paper or report under `data/`, named `<first-author-surname>-<short-name>-<year>.toml` (for a report without named authors, use the organization). Run `python3 build.py` and commit the regenerated `README.md` with it. Every pull request runs `python3 build.py --check`, which rejects missing or unknown fields, duplicates, and a README that was not rebuilt.

## What belongs here

An entry needs all three:

1. **An LLM or an LLM-based agent does the optimizing.** LLM-guided evolutionary or tree search counts. Machine learning for systems without an LLM (reinforcement-learning schedulers, Bayesian-optimization tuners, learned cost models) does not.
2. **The thing optimized or evaluated sits above a single kernel, in the stack that trains or serves models.** That covers end-to-end inference or training performance; serving engines and training frameworks, their code or their configuration, including engines and trainers that an agent builds; ML compilers; configuration for ML workloads (parallelism, launch flags, batching, KV cache, scheduling and routing policies, collective communication, cluster scheduling of ML jobs, MoE expert placement); and benchmarks that measure LLMs or agents on these tasks.
3. **Kernel work needs an end-to-end measurement.** A kernel that an agent writes or tunes qualifies when its gain is measured at the model level in a real framework: throughput, latency or time to train. Single-kernel generation and optimization belongs in the kernel lists linked from the README.

Not included:

- infrastructure built for agents (agent runtimes, sandboxes, memory, tool platforms);
- ML systems designed by people, with no LLM in the optimization loop;
- general software-performance work whose targets are not ML infrastructure;
- general systems work (databases, operating systems, networking, storage) unless one of its reported case studies targets ML infrastructure;
- benchmarks whose objective is model quality rather than infrastructure performance.

How the rule applies to cases that came up:

- A general method is included when it reports a result on ML infrastructure. Its category is `method`, and the summary names the ML-infrastructure case study.
- A benchmark that mixes kernel tasks with end-to-end tasks is included, and the summary says which part is end to end.
- A general agent benchmark (research engineering, terminal tasks, combinatorial optimization) is included only when ML-infrastructure performance tasks are its focus or a named track, not one task among many.
- A benchmark of configuration data for ML systems is included even when non-LLM optimizers can also use it, as long as the paper evaluates LLMs or agents on it.

## Entry format

```toml
title = "VibeServe: Can AI Agents Build Bespoke LLM Serving Systems?"
authors = ["Keisuke Kamahori", "Shihang Li", "Simon Peter", "Baris Kasikci"]
date = 2026-05-07          # first public version: the arXiv v1 date, or the date on the publication or post
# venue = "..."           # optional, only once accepted
arxiv = "2605.06068"       # arxiv or url is required
# url = "https://..."      # the primary page of work without an arXiv id
code = "https://github.com/uw-syfi/vibesys"   # optional: the official repository
category = "serving"       # serving | training | compiler | benchmark | method
summary = "One sentence: what is optimized, what the LLM or agent does, and how it is evaluated end to end."
result = "Optional: the headline result as the authors report it, with its setting."
```

## Checking an entry

- Take the title, authors and date from the primary source: the arXiv abstract page (use the v1 date), the publication's own page, or a dated announcement of it in the authors' own repository (a release or a commit). If the date cannot be confirmed there, leave the entry out rather than filling it in from a secondary source.
- Give a venue only once the work is accepted, as stated by the proceedings, the venue's site or the authors.
- Quote numbers as the authors report them, with their setting: model, hardware and baseline. No ratings, and no comparisons across entries.
