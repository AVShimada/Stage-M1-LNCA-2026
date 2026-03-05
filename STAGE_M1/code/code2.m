%% ========================================================================
%  ANALYSE DES PENTES AVEC BOOTSTRAP - RETOUR AU THÈME NATIF (SOMBRE)
%% ========================================================================

%% =========================
% 1. PARAMÈTRES & DONNÉES
%% =========================
N_nodes = 68;
n_boot  = 1000;  
alpha   = 0.05;  

% Note : N et ages doivent déjà être présents dans votre workspace
strength_FC     = zeros(N, N_nodes);
strength_SC_raw = zeros(N, N_nodes);
strength_SC_log = zeros(N, N_nodes);

fprintf('Calcul des forces pour %d sujets...\n', N);

for i = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    temp_FC = SUBJECT.FC;
    temp_SC = SUBJECT.SC;
    
    temp_FC(1:N_nodes+1:end) = 0;
    temp_SC(1:N_nodes+1:end) = 0;
    
    strength_FC(i,:)     = sum(temp_FC, 2);
    strength_SC_raw(i,:) = sum(temp_SC, 2);
    strength_SC_log(i,:) = sum(log(temp_SC + 1), 2);
end

%% =========================
% 2. RÉGRESSIONS ORIGINALES
%% =========================
X_orig = [ones(N,1), ages];
b_FC_orig  = X_orig \ strength_FC;
b_raw_orig = X_orig \ strength_SC_raw;
b_log_orig = X_orig \ strength_SC_log;

slopes_FC     = b_FC_orig(2,:)';
slopes_SC_raw = b_raw_orig(2,:)';
slopes_SC_log = b_log_orig(2,:)';

%% ==========================================
% 3. MOTEUR BOOTSTRAP
%% ==========================================
boot_slopes_FC  = zeros(n_boot, N_nodes);
boot_slopes_raw = zeros(n_boot, N_nodes);
boot_slopes_log = zeros(n_boot, N_nodes);

fprintf('Lancement du Bootstrap (%d itérations)...\n', n_boot);

for b = 1:n_boot
    idx = randi(N, [N, 1]); 
    X_resampled = [ones(N,1), ages(idx)];
    
    b_FC  = X_resampled \ strength_FC(idx, :);
    b_raw = X_resampled \ strength_SC_raw(idx, :);
    b_log = X_resampled \ strength_SC_log(idx, :);
    
    boot_slopes_FC(b, :)  = b_FC(2, :);
    boot_slopes_raw(b, :) = b_raw(2, :);
    boot_slopes_log(b, :) = b_log(2, :);
end

CI_FC  = prctile(boot_slopes_FC, [2.5, 97.5]);
CI_raw = prctile(boot_slopes_raw, [2.5, 97.5]);
CI_log = prctile(boot_slopes_log, [2.5, 97.5]);

err_FC  = [slopes_FC' - CI_FC(1,:);  CI_FC(2,:)  - slopes_FC'];
err_raw = [slopes_SC_raw' - CI_raw(1,:); CI_raw(2,:) - slopes_SC_raw'];
err_log = [slopes_SC_log' - CI_log(1,:); CI_log(2,:) - slopes_SC_log'];

% Couleur pour les barres d'erreur (Gris clair pour être visible sur fond sombre)
errCol = [0.8 0.8 0.8]; 

%% ==========================================
% 4. VISUALISATION : SC (RAW VS LOG)
%% ==========================================
figure('Name', 'Pentes SC : Bootstrap');

% --- SC RAW ---
subplot(2,1,1); hold on;
sig_raw = (CI_raw(1,:) > 0 | CI_raw(2,:) < 0);
b1 = bar(1:N_nodes, slopes_SC_raw, 'FaceColor', [0.2 0.6 0.8], 'EdgeColor', 'none');
b1.FaceColor = 'flat';
b1.CData(sig_raw,:) = repmat([0.8 0.2 0.2], sum(sig_raw), 1);
errorbar(1:N_nodes, slopes_SC_raw, err_raw(1,:), err_raw(2,:), '.', 'Color', errCol, 'LineWidth', 0.5);
title('Pentes SC Raw (Rouge = Significatif)');
grid on; ylabel('Pente');

% --- SC LOG ---
subplot(2,1,2); hold on;
sig_log = (CI_log(1,:) > 0 | CI_log(2,:) < 0);
b2 = bar(1:N_nodes, slopes_SC_log, 'FaceColor', [0.8 0.5 0.2], 'EdgeColor', 'none');
b2.FaceColor = 'flat';
b2.CData(sig_log,:) = repmat([0.8 0.2 0.2], sum(sig_log), 1);
errorbar(1:N_nodes, slopes_SC_log, err_log(1,:), err_log(2,:), '.', 'Color', errCol, 'LineWidth', 0.5);
title('Pentes SC Log (Rouge = Significatif)');
xlabel('Nœuds'); ylabel('Pente');
grid on;

%% ==========================================
% 5. VISUALISATION : FC
%% ==========================================
figure('Name', 'Pentes FC : Bootstrap');
hold on;
sig_FC = (CI_FC(1,:) > 0 | CI_FC(2,:) < 0);
b3 = bar(1:N_nodes, slopes_FC, 'FaceColor', [0.4 0.4 0.4], 'EdgeColor', 'none');
b3.FaceColor = 'flat';
b3.CData(sig_FC,:) = repmat([0.8 0.2 0.2], sum(sig_FC), 1);
errorbar(1:N_nodes, slopes_FC, err_FC(1,:), err_FC(2,:), '.', 'Color', errCol, 'LineWidth', 0.5);
title('Pentes FC (Rouge = Significatif)');
xlabel('Nœuds'); ylabel('Pente');
grid on;

%% =========================
% 6. COURBES LISSÉES (LOESS)
%% =========================
[ages_sorted, idx_s] = sort(ages);

figure('Name', 'LOESS Evolution FC'); hold on;
for n = 1:N_nodes
    y_smooth = smooth(ages_sorted, strength_FC(idx_s, n), 0.3, 'loess');
    plot(ages_sorted, y_smooth, 'LineWidth', 1);
end
title('Évolution des 68 nœuds FC (LOESS)');
xlabel('Âge'); ylabel('Force FC'); grid on;

figure('Name', 'LOESS Evolution SC Log'); hold on;
for n = 1:N_nodes
    y_smooth = smooth(ages_sorted, strength_SC_log(idx_s, n), 0.3, 'loess');
    plot(ages_sorted, y_smooth, 'LineWidth', 1);
end
title('Évolution des 68 nœuds SC (log, LOESS)');
xlabel('Âge'); ylabel('Force SC (log)'); grid on;