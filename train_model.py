import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.decomposition import PCA
import time  
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)  
import random
from datetime import datetime, timedelta
import pickle

"""
Network Attack Detection Model Training
Using GHF-ART (Gradient Harmonized Forest with Adaptive Resonance Theory)
"""
class GHF_ART_Optimized:
    """
    Optimized GHF-ART (Generalized Hierarchical Fuzzy Adaptive Resonance Theory) Clustering Algorithm

    This implementation uses vectorized operations and efficient data structures for improved performance.
    """

    def __init__(self, alpha: float = 0.01, beta: float = 0.6, rho0: float = 0.6, epsilon: float = 0.001):
        """
        Initialize GHF-ART clustering algorithm

        Args:
            alpha: Small constant for choice function denominator
            beta: Learning rate for weight updates
            rho0: Baseline vigilance parameter for all channels
            epsilon: Small value for vigilance updates
        """
        self.alpha = alpha
        self.beta = beta
        self.rho0 = rho0
        self.epsilon = epsilon

        # Algorithm state variables
        self.K = None  # Number of feature channels
        self.m = None  # Number of documents
        self.J = None  # Number of clusters
        self.weights = None  # Cluster weights (K x max_clusters x 2)
        self.gamma = None  # Contribution parameters
        self.rho = None  # Vigilance parameters
        self.Assign = None  # Cluster assignments
        self.L = None  # Cluster sizes
        self.Dj_k = None  # Cluster-specific differences
        self.D_k = None  # Overall differences
        self.R_k = None  # Robustness for each channel

        # Pre-allocated arrays for efficiency
        self.max_clusters = 1000  # Pre-allocate space

    def complement_coding(self, df: pd.DataFrame) -> np.ndarray:
        """
        Apply complement coding to all columns at once using vectorization

        Args:
            df: Normalized dataframe of size m x n (values in [0, 1])

        Returns:
            Complement-coded feature array of shape (K, m, 2)
        """
        data = df.values  # Convert to numpy array once
        # Stack original and complement (1 - original) along last axis
        complement_coded = np.stack([data, 1 - data], axis=-1)  # Shape: (m, K, 2)
        return np.transpose(complement_coded, (1, 0, 2))  # Shape: (K, m, 2)

    def choice_function_vectorized(self, I_n: np.ndarray, n: int) -> np.ndarray:
        """
        Compute choice function for all clusters simultaneously

        Args:
            I_n: Input patterns of shape (K, m, 2)
            n: Document index

        Returns:
            Choice function values for all active clusters
        """
        if self.J == 0:
            return np.array([])

        # Get input pattern for document n: shape (K, 2)
        x_n = I_n[:, n, :]  # Shape: (K, 2)

        # Get active weights: shape (K, J, 2)
        active_weights = self.weights[:, :self.J, :]

        # Compute intersections for all clusters at once
        # Broadcast x_n (K, 1, 2) with active_weights (K, J, 2)
        intersections = np.minimum(x_n[:, np.newaxis, :], active_weights)  # Shape: (K, J, 2)

        # Sum intersections along last axis: shape (K, J)
        intersection_sums = np.sum(intersections, axis=2)

        # Compute denominators: alpha + sum(|weights|)
        weight_norms = np.sum(np.abs(active_weights), axis=2)  # Shape: (K, J)
        denominators = self.alpha + weight_norms

        # Compute numerators with gamma weighting
        numerators = self.gamma[:, np.newaxis] * intersection_sums  # Shape: (K, J)

        # Compute choice function values
        T_values = np.sum(numerators / denominators, axis=0)  # Shape: (J,)

        return T_values

    def match_function_vectorized(self, I_n: np.ndarray, n: int, cluster_indices: np.ndarray) -> np.ndarray:
        """
        Compute match function for specified clusters and all channels

        Args:
            I_n: Input patterns of shape (K, m, 2)
            n: Document index
            cluster_indices: Array of cluster indices to compute matches for

        Returns:
            Match values of shape (len(cluster_indices), K)
        """
        if len(cluster_indices) == 0:
            return np.array([]).reshape(0, self.K)

        # Get input pattern for document n: shape (K, 2)
        x_n = I_n[:, n, :]

        # Get weights for specified clusters: shape (K, len(cluster_indices), 2)
        selected_weights = self.weights[:, cluster_indices, :]

        # Compute intersections
        intersections = np.minimum(x_n[:, np.newaxis, :], selected_weights)
        intersection_sums = np.sum(intersections, axis=2)  # Shape: (K, len(cluster_indices))

        # Compute denominators (input norms)
        x_norms = np.sum(np.abs(x_n), axis=1)  # Shape: (K,)

        # Avoid division by zero
        denominators = np.where(x_norms > 0, x_norms, 1.0)

        # Compute match values
        match_values = intersection_sums / denominators[:, np.newaxis]  # Shape: (K, len(cluster_indices))

        # Set to 0 where denominator was 0
        match_values = np.where(x_norms[:, np.newaxis] > 0, match_values, 0.0)

        return match_values.T  # Shape: (len(cluster_indices), K)

    def update_weights_vectorized(self, cluster_j: int, I_n: np.ndarray, n: int) -> np.ndarray:
        """
        Update cluster weights using vectorized operations

        Args:
            cluster_j: Cluster index
            I_n: Input patterns of shape (K, m, 2)
            n: Document index

        Returns:
            Old weights for difference calculation
        """
        # Store old weights
        old_weights = self.weights[:, cluster_j, :].copy()  # Shape: (K, 2)

        # Get input pattern
        x_n = I_n[:, n, :]  # Shape: (K, 2)

        # Compute intersections
        intersections = np.minimum(x_n, old_weights)

        # Update weights: beta * intersection + (1-beta) * old_weights
        self.weights[:, cluster_j, :] = self.beta * intersections + (1 - self.beta) * old_weights

        return old_weights

    def update_differences_and_contributions_vectorized(self, cluster_j: int, I_n: np.ndarray,
                                                      n: int, old_weights: np.ndarray) -> None:
        """
        Update cluster differences and contribution parameters using vectorized operations

        Args:
            cluster_j: Cluster index
            I_n: Input patterns of shape (K, m, 2)
            n: Document index
            old_weights: Previous weights of shape (K, 2)
        """
        # Current weights
        new_weights = self.weights[:, cluster_j, :]  # Shape: (K, 2)

        # Compute norms
        w_norms = np.sum(np.abs(new_weights), axis=1)  # Shape: (K,)
        w_old_norms = np.sum(np.abs(old_weights), axis=1)  # Shape: (K,)

        # Input pattern
        x_n = I_n[:, n, :]  # Shape: (K, 2)

        # Compute weight changes and pattern differences
        weight_changes = np.sum(np.abs(old_weights - new_weights), axis=1)  # Shape: (K,)
        pattern_diffs = np.sum(np.abs(new_weights - x_n), axis=1)  # Shape: (K,)

        # Update cluster differences (vectorized)
        valid_mask = (w_norms > 0) & (w_old_norms > 0)

        updates = (w_old_norms * self.Dj_k[cluster_j, :] +
                  weight_changes +
                  pattern_diffs / self.L[cluster_j])

        self.Dj_k[cluster_j, valid_mask] = updates[valid_mask]

        # Update overall differences
        if self.J > 0:
            self.D_k = np.mean(self.Dj_k[:self.J, :], axis=0)

        # Update robustness and contribution parameters
        self.R_k = np.exp(-self.D_k)
        R_sum = np.sum(self.R_k)
        if R_sum > 0:
            self.gamma = self.R_k / R_sum

    def create_new_cluster(self, I_n: np.ndarray, n: int) -> None:
        """
        Create a new cluster with the current input pattern

        Args:
            I_n: Input patterns of shape (K, m, 2)
            n: Document index
        """
        # Expand arrays if needed
        if self.J >= self.weights.shape[1]:
            new_size = max(self.J + 1, self.weights.shape[1] * 2)

            # Expand weights
            new_weights = np.zeros((self.K, new_size, 2))
            new_weights[:, :self.weights.shape[1], :] = self.weights
            self.weights = new_weights

            # Expand other arrays
            new_L = np.zeros(new_size)
            new_L[:len(self.L)] = self.L
            self.L = new_L

            new_Dj_k = np.zeros((new_size, self.K))
            new_Dj_k[:self.Dj_k.shape[0], :] = self.Dj_k
            self.Dj_k = new_Dj_k

        # Set weights for new cluster
        self.weights[:, self.J, :] = I_n[:, n, :]

        # Set cluster size and assignment
        self.L[self.J] = 1
        self.Assign[n] = self.J

        # Increment cluster count
        self.J += 1

        # Update contribution parameters
        if self.J > 1:
            power = self.J / (self.J + 1)
            R_powered = np.power(self.R_k, power)
            R_sum = np.sum(R_powered)
            if R_sum > 0:
                self.gamma = R_powered / R_sum

    def fit(self, df: pd.DataFrame) -> np.ndarray:
        """
        Fit the GHF-ART clustering algorithm to the data

        Args:
            df: Input dataframe of size m x n (already normalized to [0, 1])

        Returns:
            Cluster assignments array
        """
        self.m, self.K = df.shape

        # Apply complement coding (vectorized)
        I = self.complement_coding(df)  # Shape: (K, m, 2)

        # Initialize arrays
        self.weights = np.zeros((self.K, self.max_clusters, 2))
        self.Assign = np.zeros(self.m, dtype=int)
        self.L = np.zeros(self.max_clusters)
        self.Dj_k = np.zeros((self.max_clusters, self.K))
        self.D_k = np.zeros(self.K)
        self.R_k = np.ones(self.K)
        self.gamma = np.ones(self.K) / self.K

        # Initialize first cluster
        self.J = 1
        self.weights[:, 0, :] = I[:, 0, :]
        self.Assign[0] = 0
        self.L[0] = 1

        # Pre-compute batch operations where possible
        rho_base = np.full(self.K, self.rho0)

        # Main clustering loop
        for n in range(1, self.m):
            self.rho = rho_base.copy()

            max_attempts = self.J + 1
            attempts = 0
            excluded_clusters = set()

            while attempts < max_attempts:
                # Get valid clusters
                valid_clusters = [j for j in range(self.J) if j not in excluded_clusters]

                if not valid_clusters:
                    self.create_new_cluster(I, n)
                    break

                # Compute choice function for valid clusters
                valid_indices = np.array(valid_clusters)
                choice_values = self.choice_function_vectorized(I, n)
                valid_choice_values = choice_values[valid_indices]

                # Find winner
                best_idx = np.argmax(valid_choice_values)
                winner = valid_clusters[best_idx]

                # Check match conditions
                match_values = self.match_function_vectorized(I, n, np.array([winner]))[0]  # Shape: (K,)

                # Vectorized vigilance check
                resonance_mask = match_values >= self.rho

                if np.all(resonance_mask):
                    # Resonance achieved
                    old_weights = self.update_weights_vectorized(winner, I, n)
                    self.Assign[n] = winner
                    self.L[winner] += 1
                    self.update_differences_and_contributions_vectorized(winner, I, n, old_weights)
                    break
                else:
                    # Update vigilance for failed channels
                    failed_channels = ~resonance_mask
                    self.rho[failed_channels] = match_values[failed_channels] + self.epsilon
                    excluded_clusters.add(winner)

                attempts += 1

        return self.Assign[:self.m].copy()

    def get_cluster_info(self) -> dict:
        """
        Get information about the clustering results

        Returns:
            Dictionary with clustering information
        """
        if self.Assign is None:
            return {"error": "Algorithm not fitted yet"}

        active_clusters = np.arange(self.J)
        cluster_sizes = self.L[:self.J].astype(int).tolist()

        return {
            "n_clusters": self.J,
            "cluster_sizes": cluster_sizes,
            "total_documents": self.m,
            "n_channels": self.K,
            "contribution_weights": self.gamma.tolist() if self.gamma is not None else None,
            "vigilance_parameters": self.rho.tolist() if self.rho is not None else None
        }

    def predict(self, test_df: pd.DataFrame) -> Tuple[List[int], List[float]]:
        """
        Predict cluster assignments for test data using vectorized operations

        Args:
            test_df: Test samples of shape (n_samples, n_channels)
                     Already normalized to [0, 1] range

        Returns:
            predictions: Predicted cluster indices or -1 for anomaly
            scores: Anomaly scores (higher = more anomalous)
        """
        if self.weights is None or self.J is None:
            raise ValueError("Model must be fitted before making predictions")

        if test_df.shape[1] != self.K:
            raise ValueError(f"Test data has {test_df.shape[1]} channels, but model was trained with {self.K} channels")

        # Complement code test data
        I_test = self.complement_coding(test_df)  # Shape: (K, n_test, 2)
        n_test_samples = test_df.shape[0]

        predictions = []
        scores = []

        # Process in batches for better memory efficiency
        batch_size = min(100, n_test_samples)

        for start_idx in range(0, n_test_samples, batch_size):
            end_idx = min(start_idx + batch_size, n_test_samples)
            batch_indices = range(start_idx, end_idx)

            for n in batch_indices:
                rho_local = np.full(self.K, self.rho0)

                # Compute choice function for all clusters
                choice_values = self.choice_function_vectorized(I_test, n)

                if len(choice_values) == 0:
                    predictions.append(-1)
                    scores.append(1.0)
                    continue

                # Compute match values for all clusters
                all_clusters = np.arange(self.J)
                match_matrix = self.match_function_vectorized(I_test, n, all_clusters)  # Shape: (J, K)

                # Find clusters that pass vigilance test
                vigilance_mask = np.all(match_matrix >= rho_local[np.newaxis, :], axis=1)  # Shape: (J,)

                if np.any(vigilance_mask):
                    # Among resonating clusters, pick the one with highest choice function
                    valid_choice_values = np.where(vigilance_mask, choice_values, -np.inf)
                    best_cluster = np.argmax(valid_choice_values)

                    predictions.append(best_cluster)

                    # Compute anomaly score
                    best_match_values = match_matrix[best_cluster]  # Shape: (K,)
                    weighted_match = np.sum(self.gamma * best_match_values)
                    score = 1.0 - weighted_match
                else:
                    predictions.append(-1)
                    score = 1.0

                scores.append(score)

        return predictions, scores


# Main execution block
if __name__ == "__main__":
    # 1) Load & Label Data
    print("Loading KDD dataset...")
    names = [
        'duration','protocol_type','service','flag','src_bytes','dst_bytes','land','wrong_fragment',
        'urgent','hot','num_failed_logins','logged_in','num_compromised','root_shell','su_attempted',
        'num_root','num_file_creations','num_shells','num_access_files','num_outbound_cmds',
        'is_host_login','is_guest_login','count','srv_count','serror_rate','srv_serror_rate',
        'rerror_rate','srv_rerror_rate','same_srv_rate','diff_srv_rate','srv_diff_host_rate',
        'dst_host_count','dst_host_srv_count','dst_host_same_srv_rate','dst_host_diff_srv_rate',
        'dst_host_same_src_port_rate','dst_host_srv_diff_host_rate','dst_host_serror_rate',
        'dst_host_srv_serror_rate','dst_host_rerror_rate',        'dst_host_srv_rerror_rate','label'
    ]
    df = pd.read_csv(
    "kddcup.data_10_percent_corrected",
    header=None,
        names=names
    )
    df['label'] = df['label'].apply(lambda x: 'normal' if x == 'normal.' else 'attack')

    # Drop rows with any NaN values
    df.dropna(inplace=True)

    # 2) Prepare features & labels
    print("Preprocessing features...")
    X_raw = df.drop('label', axis=1)
    y_all = (df['label'] == 'normal').astype(int)  # 1 = normal, 0 = attack

    cat_cols = ['protocol_type','service','flag']
    enc = OneHotEncoder(sparse_output=False)
    X_cat = enc.fit_transform(X_raw[cat_cols])
    X_num = X_raw.drop(cat_cols, axis=1).values

    scaler = MinMaxScaler()
    X_num_scaled = scaler.fit_transform(X_num)
    X_all = np.hstack([X_num_scaled, X_cat])

    # 2.5) Create dataframe with features and labels
    df_features = pd.DataFrame(X_all)
    df_features['label'] = y_all.values

    # 3) Separate full normal and attack datasets
    print("Separating full normal and attack datasets...")
    normal_df = df_features[df_features['label'] == 1]
    attack_df = df_features[df_features['label'] == 0]

    # Train on all normal data
    X_train = normal_df.drop('label', axis=1)

    # Sample equal number of attack samples
    attack_sample = attack_df.sample(n=len(X_train), random_state=42, replace=True)
    X_test = attack_sample.drop('label', axis=1)
    y_test_true = attack_sample['label'].values

    print(f"Training samples (normal): {len(X_train)}")
    print(f"Testing samples (attack): {len(X_test)}")

    # 4) Fit GHF_ART (unsupervised)
    print("\nStarting GHF-ART training...")
    start_time = time.time()

    ghf_art = GHF_ART_Optimized(alpha=0.01, beta=1, rho0=0.1, epsilon=0.001)
    assignments = ghf_art.fit(X_train)

    end_time = time.time()
    print(f"GHF-ART training complete in {end_time - start_time:.2f} seconds.")
    print(f"Total clusters formed: {ghf_art.J}") # Fixed from len(ghf_art.weights)

    # Save the trained model, scaler, and encoder for real-time monitoring
    print("\nSaving trained model...")
    model_data = {
        'model': ghf_art,
        'scaler': scaler,
        'encoder': enc
    }
    with open('ghf_art_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    print("✅ Model saved to 'ghf_art_model.pkl'")

    # 5) Predict (−1 marks anomaly/attack)
    print("\nScoring attack samples...")
    pred_clusters, pred_scores = ghf_art.predict(X_test)
    # y_pred = np.array(pred_clusters) != -1  # Should ideally all be False
    # 6) Accuracy (expecting 0% predicted as normal)
    n_attack = len(y_test_true)
    n_detected_anomalies = sum(pred == -1 for pred in pred_clusters)
    accuracy = n_detected_anomalies / n_attack
    print(f"Anomalies detected: {n_detected_anomalies} out of {n_attack} ({accuracy*100:.2f}%)")
    # --- Evaluation using only binary outputs (no pred_scores) ---


    # 1 = attack (anomaly), 0 = normal
    y_true = 1 - y_test_true.astype(int)
    y_pred = np.array(pred_clusters) == -1   # True = predicted anomaly

    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    acc       = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall    = recall_score(y_true, y_pred, zero_division=0)
    f1        = f1_score(y_true, y_pred, zero_division=0)

    print("=== Binary Anomaly Detection Metrics ===")
    print(f"Accuracy : {acc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-Score : {f1:.4f}")

    print("\nConfusion Matrix (attack = 1)")
    print("      Pred 0  Pred 1")
    print(f"True 0   {tn}    {fp}")
    print(f"True 1   {fn}    {tp}")

    print("\nClassification Report")
    print(classification_report(y_true, y_pred, target_names=["Normal", "Attack"]))

    # 7) Visualization
    print("Reducing dimensions for visualization...")
    pca = PCA(n_components=2)
    X_combined = pd.concat([X_train, X_test])
    y_combined = np.concatenate([np.ones(len(X_train)), np.zeros(len(X_test))])
    X2d = pca.fit_transform(X_combined)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,5))
    ax1.scatter(X2d[:len(X_train),0], X2d[:len(X_train),1], c='blue', s=2, label='Normal')
    ax1.scatter(X2d[len(X_train):,0], X2d[len(X_train):,1], c='red', s=2, label='Attack')
    ax1.set_title("True: Normal vs Attack")
    ax1.set_xlabel("PC1"); ax1.set_ylabel("PC2")
    ax1.legend()

    ax2.scatter(X2d[len(X_train):,0], X2d[len(X_train):,1], c=["red" if p==-1 else "blue" for p in pred_clusters], s=2)
    ax2.set_title("GHF-ART: Detected Normal vs Anomaly")
    ax2.set_xlabel("PC1"); ax2.set_ylabel("PC2")

    plt.tight_layout()
    plt.show()  

    # STEP : NLP Log Generation & Data Enrichment
    print("\nGenerating NLP Logs and preparing Dashboard Data...")

    # 1. Reconstruct a DataFrame for the Test set (Attacks)
    # We need the original unscaled values to write meaningful logs
    # We use the index from attack_sample to retrieve original data
    test_indices = attack_sample.index
    original_test_data = df.loc[test_indices].copy()

    # 2. Add Predictions and Scores
    original_test_data['anomaly_prediction'] = pred_clusters # -1 is anomaly
    original_test_data['anomaly_score'] = pred_scores

    # 3. Synthetic Data Injection (To make the Dashboard realistic)
    # Since KDD 99 doesn't have IPs or Timestamps, we simulate them for the UI.
    def generate_ip():
        return f"192.168.1.{random.randint(2, 254)}"

    def generate_timestamp():
        # Random time within the last 24 hours
        now = datetime.now()
        delta = random.randint(0, 86400)
        return now - timedelta(seconds=delta)

    original_test_data['src_ip'] = [generate_ip() for _ in range(len(original_test_data))]
    original_test_data['dst_ip'] = [f"10.0.0.{random.randint(2, 100)}" for _ in range(len(original_test_data))]
    original_test_data['timestamp'] = [generate_timestamp() for _ in range(len(original_test_data))]

    # 4. NLP Log Generator Function
    def generate_nlp_log(row):
        """
        Converts a row of data into a human-readable NLP summary.
        Targeting: Source -> Dest interaction context.
        """
        status = "CRITICAL ANOMALY" if row['anomaly_prediction'] == -1 else "Normal Traffic"

        # Rule-based NLP generation
        log_message = (
            f"[{status}] {row['protocol_type'].upper()} connection from {row['src_ip']} "
            f"to {row['dst_ip']} on service '{row['service']}'. "
        )

        if row['anomaly_prediction'] == -1:
            log_message += f"Suspicious activity detected. "
            if row['src_bytes'] > 10000:
                log_message += f"Unusually high data transfer ({row['src_bytes']} bytes). "
            if row['count'] > 50:
                log_message += f"High connection count ({row['count']}) indicating potential Denial of Service (DoS). "
            if row['logged_in'] == 0 and row['service'] == 'http':
                log_message += f"Attempted HTTP access without login. "

            log_message += f"Severity Score: {row['anomaly_score']:.4f}."
        else:
            log_message += "Pattern matches known normal behavior."

        return log_message

    original_test_data['nlp_log'] = original_test_data.apply(generate_nlp_log, axis=1)

    # 5. Save for Streamlit
    # We only save the anomalies and a few normal samples to keep the file size manageable for the demo
    output_df = original_test_data.sort_values(by='timestamp', ascending=False)
    output_df.to_csv("network_logs_processed.csv", index=False)

    print("Success! Data saved to 'network_logs_processed.csv'.")
    print("Sample NLP Log:", output_df.iloc[0]['nlp_log'])