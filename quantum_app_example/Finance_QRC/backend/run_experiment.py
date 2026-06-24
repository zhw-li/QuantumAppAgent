"""
Finance QRC 实验运行器

端到端执行 QRC vs Classic RC 股票价格预测实验:
1. 加载真实股票数据 (yfinance)
2. 构建 QRC 和 ClassicRC 模型
3. 训练与预测
4. 计算评估指标 (RMSE, MAE, MAPE)
5. 保存结果到 JSON

使用方法:
    python run_experiment.py                           # 默认: AAPL, 4 qubits, depth=2, window=5
    python run_experiment.py --tickers AAPL MSFT       # 指定股票
    python run_experiment.py --n_qubits 6 --depth 3    # 量子参数
    python run_experiment.py --window_size 10           # 窗口大小
    python run_experiment.py --all_stocks               # 运行全部DOW10
"""

import argparse
import json
import os
import sys
import time
import numpy as np

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import DOW10_TICKERS, TIER_DEMO, TIER_STANDARD, TIER_FULL, load_all_stocks
from qrc_model import QuantumRC, ClassicRC, compute_metrics


# 项目根目录 (自动检测: 优先使用环境变量, 否则基于脚本位置)
_PROJECT_ROOT = os.environ.get("FINANCE_QRC_ROOT", 
                               os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_ARTIFACTS_DIR = os.path.join(_PROJECT_ROOT, "artifacts")
DEFAULT_DATA_CACHE_DIR = os.path.join(_PROJECT_ROOT, "data", "cache")


def run_single_experiment(ticker, dataset, n_qubits=4, reservoir_depth=2,
                          window_size=5, n_reservoir=100, seed=42):
    """
    对单只股票运行 QRC vs Classic RC 实验
    
    Args:
        ticker: 股票代码
        dataset: StockDataset 对象
        n_qubits: QRC 量子比特数
        reservoir_depth: QRC 储备池深度
        window_size: 滑动窗口大小
        n_reservoir: ClassicRC 储备池节点数
        seed: 随机种子
    
    Returns:
        dict: 实验结果
    """
    print(f"\n{'='*60}")
    print(f"实验: {ticker} (qubits={n_qubits}, depth={reservoir_depth}, "
          f"window={window_size}, seed={seed})")
    print(f"{'='*60}")
    
    X_train, y_train = dataset.X_train, dataset.y_train
    X_test, y_test = dataset.X_test, dataset.y_test
    
    result = {
        'ticker': ticker,
        'n_qubits': n_qubits,
        'reservoir_depth': reservoir_depth,
        'window_size': window_size,
        'n_reservoir_classic': n_reservoir,
        'seed': seed,
        'train_samples': len(X_train),
        'test_samples': len(X_test),
    }
    
    # ===== Classic RC =====
    print(f"\n--- Classic RC (reservoir={n_reservoir}) ---")
    try:
        crc = ClassicRC(n_reservoir=n_reservoir, seed=seed, spectral_radius=0.9, sparsity=0.1)
        
        t0 = time.time()
        crc.fit(X_train, y_train)
        crc_train_time = time.time() - t0
        
        t0 = time.time()
        y_pred_crc_scaled = crc.predict(X_test)
        crc_pred_time = time.time() - t0
        
        # 还原到原始价格尺度
        y_pred_crc = dataset.inverse_transform_y(y_pred_crc_scaled)
        y_test_raw = dataset.y_test_raw
        
        crc_metrics = compute_metrics(y_test_raw, y_pred_crc)
        
        result['classic_rc'] = {
            'RMSE': crc_metrics['RMSE'],
            'MAE': crc_metrics['MAE'],
            'MAPE': crc_metrics['MAPE'],
            'training_time': round(crc_train_time, 4),
            'prediction_time': round(crc_pred_time, 4),
            'n_params': int(crc.n_params),
            'n_reservoir': n_reservoir,
        }
        print(f"  RMSE={crc_metrics['RMSE']:.6f}, MAE={crc_metrics['MAE']:.6f}, "
              f"MAPE={crc_metrics['MAPE']:.4f}%")
        print(f"  训练时间={crc_train_time:.2f}s, 预测时间={crc_pred_time:.2f}s, 参数={crc.n_params}")
    except Exception as e:
        print(f"  [错误] ClassicRC 失败: {e}")
        result['classic_rc'] = {'error': str(e)}
    
    # ===== Quantum RC =====
    print(f"\n--- Quantum RC (qubits={n_qubits}, depth={reservoir_depth}) ---")
    try:
        qrc = QuantumRC(n_qubits=n_qubits, reservoir_depth=reservoir_depth, seed=seed)
        
        t0 = time.time()
        qrc.fit(X_train, y_train)
        qrc_train_time = time.time() - t0
        
        t0 = time.time()
        y_pred_qrc_scaled = qrc.predict(X_test)
        qrc_pred_time = time.time() - t0
        
        # 还原到原始价格尺度
        y_pred_qrc = dataset.inverse_transform_y(y_pred_qrc_scaled)
        
        qrc_metrics = compute_metrics(y_test_raw, y_pred_qrc)
        
        result['quantum_rc'] = {
            'RMSE': qrc_metrics['RMSE'],
            'MAE': qrc_metrics['MAE'],
            'MAPE': qrc_metrics['MAPE'],
            'training_time': round(qrc_train_time, 4),
            'prediction_time': round(qrc_pred_time, 4),
            'n_params': int(qrc.n_params),
            'n_qubits': n_qubits,
            'reservoir_depth': reservoir_depth,
            'circuit_params': qrc.count_circuit_params(),
        }
        print(f"  RMSE={qrc_metrics['RMSE']:.6f}, MAE={qrc_metrics['MAE']:.6f}, "
              f"MAPE={qrc_metrics['MAPE']:.4f}%")
        print(f"  训练时间={qrc_train_time:.2f}s, 预测时间={qrc_pred_time:.2f}s, 参数={qrc.n_params}")
    except Exception as e:
        print(f"  [错误] QuantumRC 失败: {e}")
        import traceback
        traceback.print_exc()
        result['quantum_rc'] = {'error': str(e)}
    
    # ===== 比较 =====
    if 'classic_rc' in result and 'quantum_rc' in result:
        if 'error' not in result['classic_rc'] and 'error' not in result['quantum_rc']:
            crc_rmse = result['classic_rc']['RMSE']
            qrc_rmse = result['quantum_rc']['RMSE']
            if crc_rmse > 0:
                improvement = (crc_rmse - qrc_rmse) / crc_rmse * 100
            else:
                improvement = 0.0
            
            result['comparison'] = {
                'rmse_improvement_pct': round(improvement, 4),
                'qrc_better': improvement > 0,
                'param_ratio': round(result['quantum_rc']['n_params'] / result['classic_rc']['n_params'], 4),
                'speed_ratio': round(result['quantum_rc']['training_time'] / max(result['classic_rc']['training_time'], 0.001), 4),
            }
            print(f"\n  >>> QRC vs Classic: RMSE改进={improvement:+.2f}%, "
                  f"参数比={result['comparison']['param_ratio']:.4f}, "
                  f"速度比={result['comparison']['speed_ratio']:.2f}x")
    
    return result


def run_multi_seed_experiment(ticker, dataset, seeds, **kwargs):
    """
    多种子实验，计算平均指标和标准差
    
    Args:
        ticker: 股票代码
        dataset: StockDataset
        seeds: 随机种子列表
        **kwargs: 传递给 run_single_experiment 的参数
    
    Returns:
        dict: 聚合结果
    """
    results = []
    for seed in seeds:
        r = run_single_experiment(ticker, dataset, seed=seed, **kwargs)
        results.append(r)
    
    # 聚合指标
    aggregated = {'ticker': ticker, 'seeds': seeds, 'n_seeds': len(seeds)}
    for model_key in ['classic_rc', 'quantum_rc']:
        metric_vals = {}
        for r in results:
            if model_key in r and 'error' not in r[model_key]:
                for m in ['RMSE', 'MAE', 'MAPE', 'training_time']:
                    if m in r[model_key]:
                        if m not in metric_vals:
                            metric_vals[m] = []
                        metric_vals[m].append(r[model_key][m])
        
        if metric_vals:
            aggregated[model_key] = {}
            for m, vals in metric_vals.items():
                aggregated[model_key][f'{m}_mean'] = round(np.mean(vals), 6)
                aggregated[model_key][f'{m}_std'] = round(np.std(vals), 6)
    
    # 聚合比较
    improvements = [r['comparison']['rmse_improvement_pct'] 
                    for r in results 
                    if 'comparison' in r and 'rmse_improvement_pct' in r['comparison']]
    if improvements:
        aggregated['comparison'] = {
            'rmse_improvement_mean': round(np.mean(improvements), 4),
            'rmse_improvement_std': round(np.std(improvements), 4),
        }
    
    return aggregated


def main():
    parser = argparse.ArgumentParser(description='Finance QRC Experiment Runner')
    parser.add_argument('--tickers', nargs='+', default=['AAPL'],
                        help='股票代码列表')
    parser.add_argument('--all_stocks', action='store_true',
                        help='运行全部 DOW10 股票')
    parser.add_argument('--tier', choices=['demo', 'standard', 'full'], default=None,
                        help='使用预定义股票子集')
    parser.add_argument('--n_qubits', type=int, default=4,
                        help='QRC 量子比特数 (4, 6, 8)')
    parser.add_argument('--depth', type=int, default=2,
                        help='QRC 储备池深度 (2, 3)')
    parser.add_argument('--window_size', type=int, default=5,
                        help='滑动窗口大小 (5, 10, 20)')
    parser.add_argument('--n_reservoir', type=int, default=100,
                        help='ClassicRC 储备池节点数')
    parser.add_argument('--seed', type=int, default=42,
                        help='随机种子')
    parser.add_argument('--seeds', nargs='+', type=int, default=None,
                        help='多种子实验 (如: 42 123 456)')
    parser.add_argument('--start', type=str, default='2023-01-01',
                        help='数据开始日期')
    parser.add_argument('--end', type=str, default='2025-01-01',
                        help='数据结束日期')
    parser.add_argument('--output_dir', type=str, default=None,
                        help=f'结果输出目录 (默认: {DEFAULT_ARTIFACTS_DIR})')
    
    args = parser.parse_args()
    
    # 确定股票列表
    if args.all_stocks:
        tickers = DOW10_TICKERS
    elif args.tier == 'demo':
        tickers = TIER_DEMO
    elif args.tier == 'standard':
        tickers = TIER_STANDARD
    elif args.tier == 'full':
        tickers = TIER_FULL
    else:
        tickers = args.tickers
    
    # 创建输出目录
    output_dir = args.output_dir or DEFAULT_ARTIFACTS_DIR
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("Finance QRC 实验运行器")
    print("=" * 60)
    print(f"股票: {tickers}")
    print(f"QRC: qubits={args.n_qubits}, depth={args.depth}")
    print(f"ClassicRC: reservoir={args.n_reservoir}")
    print(f"窗口大小: {args.window_size}")
    print(f"数据: {args.start} ~ {args.end}")
    
    # 加载数据
    print(f"\n[1/3] 加载数据...")
    datasets = load_all_stocks(
        tickers=tickers,
        start=args.start,
        end=args.end,
        window_size=args.window_size,
        save_dir=DEFAULT_DATA_CACHE_DIR
    )
    
    if not datasets:
        print("[错误] 没有成功加载任何股票数据")
        return
    
    # 运行实验
    print(f"\n[2/3] 运行实验...")
    all_results = []
    
    for ticker, dataset in datasets.items():
        if args.seeds:
            result = run_multi_seed_experiment(
                ticker, dataset, seeds=args.seeds,
                n_qubits=args.n_qubits,
                reservoir_depth=args.depth,
                window_size=args.window_size,
                n_reservoir=args.n_reservoir,
            )
        else:
            result = run_single_experiment(
                ticker, dataset,
                n_qubits=args.n_qubits,
                reservoir_depth=args.depth,
                window_size=args.window_size,
                n_reservoir=args.n_reservoir,
                seed=args.seed,
            )
        all_results.append(result)
    
    # 保存结果
    print(f"\n[3/3] 保存结果...")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    result_file = os.path.join(
        output_dir,
        f"qrc_experiment_{timestamp}.json"
    )
    
    output = {
        'experiment_config': {
            'tickers': tickers,
            'n_qubits': args.n_qubits,
            'reservoir_depth': args.depth,
            'window_size': args.window_size,
            'n_reservoir': args.n_reservoir,
            'seeds': args.seeds if args.seeds else [args.seed],
            'data_range': f"{args.start} ~ {args.end}",
        },
        'results': all_results,
        'timestamp': timestamp,
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"结果已保存: {result_file}")
    
    # 打印汇总
    print(f"\n{'='*60}")
    print("实验汇总")
    print(f"{'='*60}")
    print(f"{'Ticker':<8} {'Model':<12} {'RMSE':>10} {'MAE':>10} {'MAPE':>10} "
          f"{'Time':>8} {'Params':>8}")
    print("-" * 70)
    
    for r in all_results:
        ticker = r['ticker']
        for model_key in ['classic_rc', 'quantum_rc']:
            if model_key in r and 'error' not in r[model_key]:
                d = r[model_key]
                rmse = d.get('RMSE', d.get('RMSE_mean', 'N/A'))
                mae = d.get('MAE', d.get('MAE_mean', 'N/A'))
                mape = d.get('MAPE', d.get('MAPE_mean', 'N/A'))
                t = d.get('training_time', d.get('training_time_mean', 'N/A'))
                p = d.get('n_params', 'N/A')
                
                rmse_s = f"{rmse:.6f}" if isinstance(rmse, (int, float)) else str(rmse)
                mae_s = f"{mae:.6f}" if isinstance(mae, (int, float)) else str(mae)
                mape_s = f"{mape:.4f}%" if isinstance(mape, (int, float)) else str(mape)
                t_s = f"{t:.2f}s" if isinstance(t, (int, float)) else str(t)
                p_s = str(p)
                
                model_name = "ClassicRC" if model_key == 'classic_rc' else "QuantumRC"
                print(f"{ticker:<8} {model_name:<12} {rmse_s:>10} {mae_s:>10} "
                      f"{mape_s:>10} {t_s:>8} {p_s:>8}")
    
    # 保存最新结果的符号链接
    latest_file = os.path.join(output_dir, "latest_result.json")
    try:
        if os.path.exists(latest_file):
            os.remove(latest_file)
        os.symlink(result_file, latest_file)
    except Exception:
        pass
    
    return all_results


if __name__ == "__main__":
    main()
