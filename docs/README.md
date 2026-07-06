<h1 align="center">🍪 Examples & Recipes</h1>

<h3 align="center">Customize your TYQA — harness it, make it yours.</h3>

| Example                                                     | Description                                                                     |
|------------------------------------------------------------|---------------------------------------------------------------------------------|
| [Quantum applications](../quantum_app_example) | Five end-to-end QAOA / VQE / QRC showcases for the TianYan quantum cloud (Finance_QAOA, MaxCut_QAOA, UC_QAOA, H2_VQE, Finance_QRC), each with classical baseline, quantum method, verification report, and SFC showcase page |
| Survey literature | Reserved recipe slot for literature-survey workflows |


| Recipe                                                     | Description                                                                     |
|------------------------------------------------------------|---------------------------------------------------------------------------------|
| [macOS 24/7 Deployment](recipes/deployment-macos-24h.md#running-tyqa-247-on-macos-telegram-bot--stt--ccproxy)   | Run the agent as an always-on service on macOS with OAuth + Telegram + STT   |

## Contributing a Recipe

See the [Contributing Guide](../CONTRIBUTING.md) for general guidelines. When adding a new recipe:

- **Use `tyqa` CLI** — recipes should work with `tyqa serve`, `tyqa config`, or `tyqa onboard`
- **Pin dependencies** — specify package extras (e.g., `pip install -e ".[telegram,stt]"`)
- **Include a README** with clear setup and usage instructions
- **Keep it focused** — each recipe should demonstrate one deployment or integration scenario
- **Add to the table** above so others can discover it
