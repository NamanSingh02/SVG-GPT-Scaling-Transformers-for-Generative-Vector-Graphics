# SVG-Language-Model-Scaling-Laws

**Name:** Naman Singh  
**Course:** NYU CS-GY 6923 Machine Learning — Spring 2026  
**Project:** SVG-GPT: Scaling Transformer Language Models for Vector Graphics

Google Drive link for notebook output files:  
https://drive.google.com/drive/folders/1dNYoKDyR3waMEc2zXVX2zozo4VGDo4-U?usp=sharing

---

## Project Overview

This project studies **scaling laws for decoder-only Transformer language models trained on SVG code**.

SVG is a structured, XML-based vector graphics format. Unlike natural language, SVG code contains strict syntax, nested tags, coordinates, paths, colors, transformations, and geometry. This makes it an interesting domain for studying language-model scaling because model outputs can be evaluated both as text and as rendered images.

The project covered five main parts:

1. SVG data preprocessing and tokenizer training
2. Standard Transformer scaling study
3. µP scaling and extrapolation
4. Best-model SVG generation and evaluation
5. Design decisions and analysis

---

## Repository Contents

```text
.
├── notebook1_svg_preprocessing_tokenizer.ipynb
├── notebook2_standard_transformer_scaling.ipynb
├── notebook3_mup_scaling_and_extrapolation.ipynb
├── notebook4_best_model_generation_evaluation_REVISED.ipynb
├── notebook5_part5_design_decisions_analysis.ipynb
└── README.md
```

The large generated files, trained checkpoints, tokenized datasets, plots, metrics, and rendered SVG outputs are stored in Google Drive:

```text
MyDrive/
  svg_gpt_scaling/
    notebook1_preprocessing/
    notebook2_standard_scaling/
    notebook3_mup_scaling/
    notebook4_generation_eval/
    final_report_assets/
```

Drive link:  
https://drive.google.com/drive/folders/1dNYoKDyR3waMEc2zXVX2zozo4VGDo4-U?usp=sharing

---

## Datasets Used

The project used `starvector/svg-icons-simple` as the primary dataset and supplemented it with additional SVG datasets to exceed the 100M-token training requirement.

Final datasets used:

- `starvector/svg-icons-simple`
- `starvector/svg-emoji-simple`
- `umuthopeyildirim/svgen-500k`

Datasets not used in the final run:

- `starvector/svg-fonts-simple`
- `starvector/svg-stack-simple`

Final token counts after preprocessing and tokenization:

| Split | Files | Tokens |
|---|---:|---:|
| Train | 255,173 | 164,389,332 |
| Validation | 2,603 | 1,657,304 |
| Test | 2,605 | 1,655,554 |

The split was done by SVG file, not by token position, to reduce data leakage.

---

## Part 1 — Data Preprocessing and Tokenization

Notebook:

```text
notebook1_svg_preprocessing_tokenizer.ipynb
```

This notebook built the SVG preprocessing pipeline.

Main steps:

- Loaded SVG datasets from HuggingFace
- Removed comments, metadata, and unnecessary whitespace
- Rounded numeric precision to reduce vocabulary noise
- Filtered SVGs that were too short or too long
- Validated SVG XML syntax
- Deduplicated cleaned SVG strings
- Trained a BPE tokenizer on the cleaned SVG corpus
- Created train/validation/test splits
- Saved tokenized `.bin` files for model training

Tokenizer choice:

- Tokenizer type: BPE
- Vocabulary size: 4096
- Reason: 4096 is within the recommended 1K–8K range and balances compression against model size. It captures common SVG syntax while keeping embedding and output layers manageable for small models.

Key output folders:

```text
notebook1_preprocessing/tokenizer/
notebook1_preprocessing/tokenized/
notebook1_preprocessing/stats/
notebook1_preprocessing/plots/
```

---

## Part 2 — Standard Transformer Scaling Study

Notebook:

```text
notebook2_standard_transformer_scaling.ipynb
```

This notebook trained a family of standard decoder-only Transformer language models.

Model sizes:

| Model | Approx. Parameters | d_model | Layers | Heads | d_ff |
|---|---:|---:|---:|---:|---:|
| Tiny | ~1M | 128 | 4 | 4 | 512 |
| Small | ~3M | 192 | 6 | 6 | 768 |
| Medium | ~12M | 384 | 6 | 6 | 1536 |
| Large | ~34M | 512 | 10 | 8 | 2048 |
| XL | ~89M | 768 | 12 | 12 | 3072 |

Training setup:

- Objective: next-token prediction
- Optimizer: AdamW
- Schedule: cosine learning-rate schedule with warmup
- Context length: 512 tokens
- Micro-batch size: 16
- Gradient accumulation steps: 4
- Effective tokens per optimizer step: 32,768
- Training duration for scaling study: exactly 1 epoch per model

A learning-rate sweep was performed on the Tiny model. The best learning rate was transferred to all larger standard models.

Main finding:

- Standard scaling improved from Tiny through Large.
- The Standard XL model became unstable under the fixed Tiny-selected learning rate.
- This caused the standard scaling-law fit to become unreliable.

Final standard validation losses:

| Model | Final Validation Loss |
|---|---:|
| Tiny | 0.9116 |
| Small | 0.8014 |
| Medium | 0.7733 |
| Large | 0.7675 |
| XL | 2.6847 |

---

## Part 3 — µP Scaling and Extrapolation

Notebook:

```text
notebook3_mup_scaling_and_extrapolation.ipynb
```

This notebook investigated whether µP improves learning-rate transfer across model widths.

Main µP changes:

- Used the `mup` package
- Used `MuReadout`
- Used `MuAdamW`
- Used `set_base_shapes`
- Modified Transformer attention scaling toward µP-style scaling
- Tuned learning rate on the smallest µP model
- Transferred the selected learning rate to larger µP models without retuning

Final µP validation losses:

| Model | Final Validation Loss |
|---|---:|
| Tiny | 0.9525 |
| Small | 0.8397 |
| Medium | 0.8242 |
| Large | 0.7958 |
| XL | 0.8297 |

Main finding:

- Standard parameterization was slightly better up to Large.
- Standard XL failed badly under fixed LR transfer.
- µP remained stable at XL scale.
- The difference between fixed LR and µP became most significant at the XL model size.

Scaling-law fit:

| Parameterization | Alpha | R² |
|---|---:|---:|
| Standard | ~0.000000056 | ~0 |
| µP | ~0.61165 | ~0.81164 |

The µP fit was used for extrapolation because it produced the more meaningful scaling curve.

10× extrapolation result:

| Quantity | Value |
|---|---:|
| Target parameter count | ~917M |
| Predicted validation loss | ~0.7894 |
| Bootstrap mean prediction | ~0.7879 |
| 95% CI | [~0.7356, ~0.8255] |

The extrapolation was treated cautiously because it was based on only five trained model sizes and predicted beyond the observed range.

---

## Part 4 — Best Model Training and SVG Generation

Notebook:

```text
notebook4_best_model_generation_evaluation_REVISED.ipynb
```

This notebook selected the best stable generation model, continued training it, and generated SVG samples.

Selected model:

```text
Standard Large
```

Reason:

- Standard Large achieved the best stable validation loss.
- Standard XL failed under fixed LR transfer.
- µP XL was stable, but its validation loss was not better than Standard Large.

Additional training:

| Metric | Value |
|---|---:|
| Additional optimizer steps | 2,500 |
| Additional tokens seen | 81,920,000 |
| Final validation loss | ~0.7143 |
| Final validation perplexity | ~2.0429 |
| Final test loss | ~0.7153 |
| Final test perplexity | ~2.0449 |

Generation setup:

- 80 unconditional SVG candidates generated from an `<svg` prefix
- 80 prefix-conditioned candidates generated from five partial SVG prompts
- Temperature sampling used
- Top-k sampling used
- Nucleus/top-p sampling used
- All candidates were evaluated quantitatively
- A curated subset was selected for qualitative report figures

Quantitative generation metrics:

| Metric | Value |
|---|---:|
| Total candidates | 160 |
| Overall XML validity rate | 28.125% |
| Overall render rate | 28.125% |
| Overall structural validity rate | 28.125% |
| Overall report-ready rate | 15.625% |
| Unconditional XML validity rate | 47.5% |
| Unconditional render rate | 47.5% |
| Unconditional report-ready rate | 31.25% |
| Prefix XML validity rate | 8.75% |
| Prefix render rate | 8.75% |
| Prefix report-ready rate | 0% |

Main qualitative finding:

- Unconditional generation was much stronger than prefix-conditioned generation.
- The model learned common SVG conventions such as `viewBox`, `<path>`, `fill`, `stroke`, and line styling attributes.
- Many outputs were syntactically valid and icon-like.
- The model still struggled with precise geometry, repeated degenerate path commands, and controlled prefix continuation.
- Prefix-conditioned generation often stopped immediately or failed to close the SVG root tag.

---

## Part 5 — Design Decisions and Analysis

Notebook:

```text
notebook5_part5_design_decisions_analysis.ipynb
```

This notebook documented the design choices and analysis required by Part 5.

It discussed:

- Why a domain-specific BPE tokenizer was used
- Why vocabulary size 4096 was selected
- Why a 512-token context window was chosen
- Why the model family used five decoder-only Transformer sizes
- Why AdamW and cosine schedule with warmup were used
- How standard scaling compared with µP scaling
- Why fixed learning-rate transfer failed at XL
- What SVG-specific syntax and visual patterns the model learned
- What limitations remained in generation and prefix completion

The main conclusion was that the model learned SVG syntax and common icon-like patterns better than it learned robust geometric structure or controlled prefix-conditioned completion.

---

## Main Results Summary

| Component | Main Result |
|---|---|
| Training tokens | 164.39M |
| Tokenizer | BPE, vocab size 4096 |
| Context length | 512 |
| Best stable model | Standard Large |
| Best Part 4 test loss | ~0.7153 |
| Best Part 4 test perplexity | ~2.0449 |
| Standard scaling issue | XL failed under fixed Tiny-selected LR |
| µP result | More stable at XL |
| Better scaling fit | µP |
| 10× extrapolated validation loss | ~0.7894 |
| Unconditional render rate | 47.5% |
| Prefix render rate | 8.75% |

---

## How to Run

The project was designed for Google Colab.

Recommended order:

1. Run Notebook 1 to preprocess data and train the tokenizer.
2. Run Notebook 2 to train standard Transformer models.
3. Run Notebook 3 to train µP models and perform extrapolation.
4. Run Notebook 4 to continue training the best model and generate SVGs.
5. Run Notebook 5 to create final design-analysis outputs.

GPU is recommended for:

```text
Notebook 2
Notebook 3
Notebook 4
```

GPU is not required for:

```text
Notebook 5
```

Notebook 1 can run on CPU, but preprocessing/tokenization can take time.

---

## Important Google Drive Outputs

The generated outputs are too large to store directly in GitHub, so they are stored in Google Drive.

Drive link:  
https://drive.google.com/drive/folders/1dNYoKDyR3waMEc2zXVX2zozo4VGDo4-U?usp=sharing

Important output folders:

```text
notebook1_preprocessing/
  tokenizer/
  tokenized/
  stats/
  plots/

notebook2_standard_scaling/
  checkpoints/
  logs/
  results/
  plots/

notebook3_mup_scaling/
  checkpoints/
  logs/
  results/
  plots/

notebook4_generation_eval/
  checkpoints/
  metrics/
  generations/
  renders/
  report_assets/

final_report_assets/
  part5_design_analysis/
```

---

## Dependencies

Main Python dependencies:

```text
torch
numpy
pandas
matplotlib
scipy
tqdm
datasets
tokenizers
lxml
cairosvg
pillow
mup
nbformat
```

Install example:

```bash
pip install torch numpy pandas matplotlib scipy tqdm datasets tokenizers lxml cairosvg pillow mup nbformat
```

---

## Notes on Reproducibility

The notebooks save important intermediate files to Google Drive so that repeated Colab runs do not require recomputing everything.

Examples of cached outputs:

- cleaned SVG files
- trained tokenizer
- tokenized `.bin` files
- training logs
- checkpoints
- scaling result CSVs
- generated SVG samples
- rendered PNG samples
- final report assets

Random seeds were set where practical, but exact generation results may still vary across GPU runtime sessions due to nondeterminism in sampling and CUDA operations.

---

## Limitations

Important limitations of this project:

- Only five model sizes were trained, so scaling-law fits are approximate.
- Each scaling model was trained for one epoch, not to full convergence.
- The Standard XL model failed under fixed learning-rate transfer.
- µP was more stable at XL but did not outperform Standard Large for final generation.
- Valid XML did not always mean visually meaningful SVG output.
- Prefix-conditioned generation remained weak.
- The 10× extrapolation should be interpreted cautiously.

---

## References

- Kaplan et al. (2020), *Scaling Laws for Neural Language Models*
- Hoffmann et al. (2022), *Training Compute-Optimal Large Language Models*
- Yang et al. (2022), *Tensor Programs V: Tuning Large Neural Networks via Zero-Shot Hyperparameter Transfer*
- Rodriguez et al. (2023), *StarVector: Generating Scalable Vector Graphics Code from Images and Text*
- Karpathy, nanoGPT
- Microsoft, µP package
