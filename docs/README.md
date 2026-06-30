<h1 align="center">🍪 Examples & Recipes</h1>

<h3 align="center">Customize your TYQA — harness it, make it yours.</h3>

| Example                                                     | Description                                                                     |
|------------------------------------------------------------|---------------------------------------------------------------------------------|
| [Quantum applications](https://github.com/tyqa/tyqa/tree/main/quantum_app_example) | Five end-to-end QAOA / VQE / QRC showcases for the TianYan quantum cloud (Finance_QAOA, MaxCut_QAOA, UC_QAOA, H2_VQE, Finance_QRC), each with classical baseline, quantum method, verification report, and SFC showcase page |
| [Survey literature](https://github.com/tyqa/tyqa/tree/main/docs/examples/survey-literature#literature-survey)   | Run with the `paper-navigator` skill to produce a bilingual, conference-grade literature survey |


| Recipe                                                     | Description                                                                     |
|------------------------------------------------------------|---------------------------------------------------------------------------------|
| [macOS 24/7 Deployment](https://github.com/tyqa/tyqa/blob/main/docs/recipes/deployment-macos-24h.md#running-tyqa-247-on-macos-telegram-bot--stt--ccproxy)   | Run the agent as an always-on service on macOS with OAuth + Telegram + STT   |

## Contributing a Recipe

See the [Contributing Guide](../CONTRIBUTING.md) for general guidelines. When adding a new recipe:

- **Use `tyqa` CLI** — recipes should work with `tyqa serve`, `tyqa config`, or `tyqa onboard` (the CLI is renamed to `tyqa` in a future version)
- **Pin dependencies** — specify package extras (e.g., `pip install -e ".[telegram,stt]"`)
- **Include a README** with clear setup and usage instructions
- **Keep it focused** — each recipe should demonstrate one deployment or integration scenario
- **Add to the table** above so others can discover it
