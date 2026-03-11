"""
Test script for data loading and preprocessing modules.

This script demonstrates the usage of DataLoader and EngagementPreprocessor
classes with the actual Globant dataset.
"""

import sys
sys.path.insert(0, 'src')

from data import DataLoader, EngagementPreprocessor
import pandas as pd

def main():
    print("=" * 80)
    print("TESTING DATA MODULES")
    print("=" * 80)

    # Path to the dataset
    data_path = r"C:\Users\miche\Documents\projects\Globant\data\data_globant_cleaned.csv"

    # ============================================================================
    # TEST 1: DataLoader
    # ============================================================================
    print("\n" + "=" * 80)
    print("TEST 1: DataLoader")
    print("=" * 80)

    loader = DataLoader()

    # Load data
    print("\n1.1 Loading CSV file...")
    df = loader.load_from_csv(data_path)
    print(f"    Loaded: {len(df):,} rows x {len(df.columns)} columns")

    # Validate schema
    print("\n1.2 Validating schema...")
    try:
        loader.validate_schema(df)
        print("    Schema validation: PASSED")
    except Exception as e:
        print(f"    Schema validation: FAILED - {e}")

    # Get data summary
    print("\n1.3 Getting data summary...")
    summary = loader.get_data_summary(df)
    print(f"    Shape: {summary['shape']['rows']:,} rows x {summary['shape']['columns']} columns")
    print(f"    Memory usage: {summary['memory_usage_mb']:.2f} MB")
    print(f"    Date range: {summary['date_range']['min']} to {summary['date_range']['max']}")
    print(f"    Unique employees: {summary['unique_counts']['Email']:,}")
    print(f"    Engagement mean: {summary['engagement_stats']['mean']:.2f}")

    # Detect quality issues
    print("\n1.4 Detecting data quality issues...")
    quality = loader.detect_data_quality_issues(df)
    print(f"    Quality score: {quality['quality_score']:.2f}%")
    print(f"    Warnings: {len(quality['warnings'])}")
    for i, warning in enumerate(quality['warnings'][:3], 1):
        print(f"      {i}. {warning}")

    # ============================================================================
    # TEST 2: EngagementPreprocessor
    # ============================================================================
    print("\n" + "=" * 80)
    print("TEST 2: EngagementPreprocessor")
    print("=" * 80)

    preprocessor = EngagementPreprocessor(verbose=True)

    # Clean data
    print("\n2.1 Cleaning data...")
    df_clean = preprocessor.clean_data(
        df,
        remove_duplicates=True,
        handle_outliers=True,
        handle_missing=True
    )
    print(f"    Clean data: {len(df_clean):,} rows")

    # Create temporal features
    print("\n2.2 Creating temporal features...")
    df_clean = preprocessor.create_temporal_features(df_clean)
    temporal_features = ['day_of_week', 'week_of_year', 'quarter', 'is_weekend']
    print(f"    Created features: {temporal_features}")

    # Create transitions
    print("\n2.3 Creating engagement transitions...")
    transitions = preprocessor.create_transitions(df_clean, min_transitions=5)
    print(f"    Total transitions: {len(transitions):,}")
    print(f"    Unique employees: {transitions['Email'].nunique():,}")
    print(f"    Avg transitions per employee: {len(transitions) / transitions['Email'].nunique():.1f}")

    # Display transition sample
    print("\n2.4 Sample transitions:")
    sample_cols = ['Email', 'current_category', 'next_category', 'days_between', 'engagement_change']
    print(transitions[sample_cols].head(10).to_string(index=False))

    # Split train/test
    print("\n2.5 Splitting train/test...")
    train, test = preprocessor.split_train_test(
        transitions,
        test_size=0.2,
        random_state=42,
        stratify_by='current_category'
    )
    print(f"    Train: {len(train):,} transitions ({len(train)/len(transitions)*100:.1f}%)")
    print(f"    Test: {len(test):,} transitions ({len(test)/len(transitions)*100:.1f}%)")

    # Category distribution
    print("\n2.6 Category distribution in train set:")
    dist = train['current_category'].value_counts(normalize=True).sort_index() * 100
    for category, percentage in dist.items():
        print(f"    {category}: {percentage:.1f}%")

    # ============================================================================
    # TEST 3: Filtering and Utilities
    # ============================================================================
    print("\n" + "=" * 80)
    print("TEST 3: Filtering and Utilities")
    print("=" * 80)

    # Filter by features
    print("\n3.1 Filtering by features (Seniority=Sr, Location=CO/ANT/MED)...")
    filtered = preprocessor.filter_by_features(
        df_clean,
        {
            'Seniority': 'Sr',
            'Location': 'CO/ANT/MED'
        }
    )
    print(f"    Filtered: {len(filtered):,} rows ({len(filtered)/len(df_clean)*100:.1f}% of data)")

    # Get unique values
    print("\n3.2 Top positions:")
    from data import get_unique_values
    positions = get_unique_values(df_clean, 'Position')
    for i, (position, count) in enumerate(list(positions.items())[:5], 1):
        print(f"    {i}. {position}: {count:,}")

    # Get correlations
    print("\n3.3 Correlations with Engagement:")
    from data import get_correlations
    correlations = get_correlations(df_clean, target='Engagement', min_correlation=0.01)
    for feature, corr in correlations.head(5).items():
        print(f"    {feature}: {corr:.3f}")

    # ============================================================================
    # SUMMARY
    # ============================================================================
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"  Original data: {len(df):,} rows")
    print(f"  Clean data: {len(df_clean):,} rows")
    print(f"  Transitions created: {len(transitions):,}")
    print(f"  Train set: {len(train):,}")
    print(f"  Test set: {len(test):,}")
    print(f"  Quality score: {quality['quality_score']:.2f}%")
    print("\n  All tests completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
