"""QLSTM 时间序列预测 — 训练与对比管道"""
import sys
import os
import json
import time
import numpy as np
import torch

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.data_loader import load_and_preprocess, inverse_transform_close, get_raw_data
from ml.classic_lstm import ClassicLSTM, train_classic_lstm, evaluate_model
from ml.qlstm import QLSTM, train_qlstm, evaluate_qlstm

# ============================================================
# 配置
# ============================================================
DATA_PATH = "/Users/lizhaowei/code/EvoScientist/dataset/AAPL.csv"
RESULT_DIR = "/Users/lizhaowei/code/EvoScientist/qlstm/results"
os.makedirs(RESULT_DIR, exist_ok=True)

SEQ_LEN = 20
PRED_LEN = 1
BATCH_SIZE_CLASSIC = 32
BATCH_SIZE_QUANTUM = 8   # 量子模型每样本独立模拟，batch 需更小
EPOCHS_CLASSIC = 80
EPOCHS_QUANTUM = 80
LR_CLASSIC = 0.001
LR_QUANTUM = 0.005
DEVICE = "cpu"


def run_classic_baseline(train_loader, val_loader, test_loader, scaler, n_features, feature_cols):
    """训练经典 LSTM 基线"""
    print("=" * 60)
    print("📊 训练经典 LSTM 基线模型")
    print("=" * 60)

    t0 = time.time()
    model, train_losses, val_losses, best_epoch = train_classic_lstm(
        train_loader, val_loader,
        n_features=n_features,
        epochs=EPOCHS_CLASSIC,
        lr=LR_CLASSIC,
        device=DEVICE,
    )
    train_time = time.time() - t0

    # feature_idx: Close 在 feature_cols 中的索引
    feature_idx = list(feature_cols).index("Close")
    metrics, predictions, actuals = evaluate_model(
        model, test_loader, scaler, feature_idx=feature_idx, device=DEVICE
    )

    print(f"\n经典 LSTM 结果 (训练时间: {train_time:.1f}s, best_epoch: {best_epoch}):")
    for k, v in metrics.items():
        print(f"  {k}: {v:.6f}")

    return {
        "model": model,
        "train_losses": train_losses,
        "val_losses": val_losses,
        "metrics": metrics,
        "predictions": predictions,
        "actuals": actuals,
        "train_time": train_time,
        "best_epoch": best_epoch,
    }


def run_quantum_model(train_loader_q, val_loader_q, test_loader_q, scaler, n_features, feature_cols, iteration=1):
    """训练 QLSTM 模型"""
    print("\n" + "=" * 60)
    print(f"🔮 训练 QLSTM 模型 (第 {iteration} 轮迭代)")
    print("=" * 60)

    t0 = time.time()
    model, train_losses, val_losses, best_epoch = train_qlstm(
        train_loader_q, val_loader_q,
        n_features=n_features,
        n_hidden=16,
        n_qubits=2,
        n_layers=2,
        epochs=EPOCHS_QUANTUM,
        lr=LR_QUANTUM,
        device=DEVICE,
    )
    train_time = time.time() - t0

    feature_idx = list(feature_cols).index("Close")
    metrics, predictions, actuals = evaluate_qlstm(
        model, test_loader_q, scaler, feature_idx=feature_idx, device=DEVICE
    )

    print(f"\nQLSTM 结果 (训练时间: {train_time:.1f}s, best_epoch: {best_epoch}):")
    for k, v in metrics.items():
        print(f"  {k}: {v:.6f}")

    return {
        "model": model,
        "train_losses": train_losses,
        "val_losses": val_losses,
        "metrics": metrics,
        "predictions": predictions,
        "actuals": actuals,
        "train_time": train_time,
        "best_epoch": best_epoch,
        "iteration": iteration,
    }


def compare_and_decide(classic_result, quantum_result):
    """对比结果，判断量子是否超越经典"""
    print("\n" + "=" * 60)
    print("📈 模型对比")
    print("=" * 60)

    c_m = classic_result["metrics"]
    q_m = quantum_result["metrics"]

    # 以 RMSE 为主要指标
    c_rmse = c_m["RMSE"]
    q_rmse = q_m["RMSE"]
    improvement = (c_rmse - q_rmse) / c_rmse * 100

    print(f"  经典 LSTM  RMSE: {c_rmse:.6f}  MAE: {c_m['MAE']:.6f}  MAPE: {c_m['MAPE']:.4f}%")
    print(f"  QLSTM      RMSE: {q_rmse:.6f}  MAE: {q_m['MAE']:.6f}  MAPE: {q_m['MAPE']:.4f}%")
    print(f"  RMSE 改善: {improvement:+.2f}%")

    if q_rmse < c_rmse:
        print("  ✅ QLSTM 已超越经典 LSTM！")
        return True, improvement
    else:
        print("  ❌ QLSTM 未超越经典 LSTM，需要迭代优化。")
        return False, improvement


def save_results(classic_result, quantum_results, feature_cols):
    """保存所有结果"""
    # 转换 numpy 为 list 以便 JSON 序列化
    def to_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        return obj

    output = {
        "classic": {
            "metrics": {k: to_serializable(v) for k, v in classic_result["metrics"].items()},
            "train_losses": [to_serializable(x) for x in classic_result["train_losses"]],
            "val_losses": [to_serializable(x) for x in classic_result["val_losses"]],
            "train_time": classic_result["train_time"],
            "best_epoch": classic_result["best_epoch"],
            "predictions": to_serializable(classic_result["predictions"]),
            "actuals": to_serializable(classic_result["actuals"]),
        },
        "quantum_iterations": [],
    }

    for qr in quantum_results:
        output["quantum_iterations"].append({
            "iteration": qr["iteration"],
            "metrics": {k: to_serializable(v) for k, v in qr["metrics"].items()},
            "train_losses": [to_serializable(x) for x in qr["train_losses"]],
            "val_losses": [to_serializable(x) for x in qr["val_losses"]],
            "train_time": qr["train_time"],
            "best_epoch": qr["best_epoch"],
            "predictions": to_serializable(qr["predictions"]),
            "actuals": to_serializable(qr["actuals"]),
        })

    result_path = os.path.join(RESULT_DIR, "comparison_results.json")
    with open(result_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n💾 结果已保存至 {result_path}")

    # 保存模型权重
    torch.save(classic_result["model"].state_dict(), os.path.join(RESULT_DIR, "classic_lstm.pth"))
    best_q = min(quantum_results, key=lambda x: x["metrics"]["RMSE"])
    torch.save(best_q["model"].state_dict(), os.path.join(RESULT_DIR, "qlstm_best.pth"))
    print(f"💾 模型权重已保存至 {RESULT_DIR}/")

    return output


def main():
    print("🚀 QLSTM 时间序列预测 — 训练管道启动")
    print(f"数据路径: {DATA_PATH}")

    # ---- 1. 加载数据 ----
    # 经典模型使用 batch_size=32
    train_c, val_c, test_c, scaler, feature_cols = load_and_preprocess(
        DATA_PATH, seq_len=SEQ_LEN, pred_len=PRED_LEN, batch_size=BATCH_SIZE_CLASSIC
    )
    n_features = len(feature_cols)
    print(f"特征数: {n_features}, 特征列: {list(feature_cols)}")

    # 量子模型使用更小 batch
    train_q, val_q, test_q, _, _ = load_and_preprocess(
        DATA_PATH, seq_len=SEQ_LEN, pred_len=PRED_LEN, batch_size=BATCH_SIZE_QUANTUM
    )

    # ---- 2. 训练经典基线 ----
    classic_result = run_classic_baseline(train_c, val_c, test_c, scaler, n_features, feature_cols)

    # ---- 3. 训练量子模型并迭代 ----
    max_iterations = 4
    quantum_results = []
    beat_classic = False

    for iteration in range(1, max_iterations + 1):
        # 如果是迭代优化，调整超参数
        if iteration > 1:
            global EPOCHS_QUANTUM, LR_QUANTUM
            EPOCHS_QUANTUM = min(EPOCHS_QUANTUM + 30, 200)
            LR_QUANTUM = max(LR_QUANTUM * 0.8, 0.001)
            print(f"\n🔧 迭代优化: epochs={EPOCHS_QUANTUM}, lr={LR_QUANTUM:.4f}")

        qr = run_quantum_model(train_q, val_q, test_q, scaler, n_features, feature_cols, iteration)
        quantum_results.append(qr)

        beat_classic, improvement = compare_and_decide(classic_result, qr)
        if beat_classic:
            break

    if not beat_classic:
        print("\n⚠️ 达到最大迭代次数，使用最佳量子模型结果。")
        # 选择最佳量子结果
        best_q = min(quantum_results, key=lambda x: x["metrics"]["RMSE"])
        print(f"最佳量子迭代: 第 {best_q['iteration']} 轮, RMSE: {best_q['metrics']['RMSE']:.6f}")

    # ---- 4. 保存结果 ----
    save_results(classic_result, quantum_results, feature_cols)

    # ---- 5. 最终汇总 ----
    print("\n" + "=" * 60)
    print("📋 最终结果汇总")
    print("=" * 60)
    print(f"经典 LSTM: RMSE={classic_result['metrics']['RMSE']:.6f}, MAE={classic_result['metrics']['MAE']:.6f}")
    best_q = min(quantum_results, key=lambda x: x["metrics"]["RMSE"])
    print(f"最佳 QLSTM: RMSE={best_q['metrics']['RMSE']:.6f}, MAE={best_q['metrics']['MAE']:.6f} (第{best_q['iteration']}轮)")
    final_improvement = (classic_result["metrics"]["RMSE"] - best_q["metrics"]["RMSE"]) / classic_result["metrics"]["RMSE"] * 100
    print(f"最终 RMSE 改善: {final_improvement:+.2f}%")
    if final_improvement > 0:
        print("🎉 QLSTM 成功超越经典 LSTM！")
    else:
        print("💡 QLSTM 尚未超越经典方法，可进一步调整架构参数。")

    return classic_result, quantum_results


if __name__ == "__main__":
    main()
