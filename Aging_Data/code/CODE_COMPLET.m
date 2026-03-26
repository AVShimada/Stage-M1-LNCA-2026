%CODE COMPLET STAGE

%% ============
% CODE 1
%% ============

load C:\Users\aure6\Downloads\Stage_M1_Github\Stage-M1-LNCA-2026\Aging_Data\data\AgingDATA_for_learning.mat
%% =========================
% PARTIE 1 : FC
%% =========================
for Nrs = 1:49
    
    SUBJECT = eval(sprintf('SUBJECT_%d', Nrs));
    
    SUBJECT.FC = corr(SUBJECT.TS);
    
    eval(sprintf('SUBJECT_%d = SUBJECT;', Nrs));
    
end

%% =========================
% PARTIE 2 : GROUPES D'ÂGE
%% =========================
N = 49;
ages = zeros(N,1);

for i = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    ages(i) = SUBJECT.age;
end

q = quantile(ages, [0.333 0.666]);

groups = zeros(N,1);

for i = 1:N
    
    if ages(i) <= q(1)
        groups(i) = 1;
    elseif ages(i) <= q(2)
        groups(i) = 2;
    else
        groups(i) = 3;
    end
    
end

for i = 1:N
    
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    SUBJECT.quartile = groups(i);
    eval(sprintf('SUBJECT_%d = SUBJECT;', i));
    
end

for k = 1:3
    fprintf('Quartile %d : %d sujets\n', k, sum(groups==k));
end


%% =========================
% PARTIE 3 : MATRICES MOYENNES
%% =========================
figure;

for k = 1:3
    
    FC_mean = zeros(68,68);
    SC_mean = zeros(68,68);
    count = 0;
    
    for i = 1:N
        
        if groups(i) == k
            
            SUBJECT = eval(sprintf('SUBJECT_%d', i));
            
            FC_mean = FC_mean + SUBJECT.FC;
            SC_mean = SC_mean + SUBJECT.SC;
            
            count = count + 1;
            
        end
        
    end
    
    FC_mean = FC_mean / count;
    SC_mean = SC_mean / count;
    
    subplot(2,3,k);
    imagesc(FC_mean);
    colorbar;
    clim([-1 1]);
    axis square;
    title(['FC moyenne - Quartile ' num2str(k)]);
    
    subplot(2,3,k+3);
    imagesc(log(SC_mean));
    colorbar;
    axis square;
    title(['SC moyenne (log) - Quartile ' num2str(k)]);
    
end


%% =========================
% PARTIE 4 : INTRA / INTER
%% =========================
left = 1:34;
right = 35:68;

intra_all = zeros(N,1);
inter_all = zeros(N,1);

for i = 1:N
    
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    FC = SUBJECT.FC;
    
    FC_LL = FC(left,left);
    FC_RR = FC(right,right);
    FC_LR = FC(left,right);
    
    mask = ~eye(34);
    
    intra = mean([mean(FC_LL(mask)), mean(FC_RR(mask))]);
    inter = mean(FC_LR(:));
    
    intra_all(i) = intra;
    inter_all(i) = inter;
    
end

% SC
intra_SC_all = zeros(N,1);
inter_SC_all = zeros(N,1);

for i = 1:N
    
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    SC = SUBJECT.SC;
    
    SC_LL = SC(left,left);
    SC_RR = SC(right,right);
    SC_LR = SC(left,right);
    
    mask = ~eye(34);
    
    intra_SC = mean([mean(SC_LL(mask)), mean(SC_RR(mask))]);
    inter_SC = mean(SC_LR(:));
    
    intra_SC_all(i) = intra_SC;
    inter_SC_all(i) = inter_SC;
    
end


%% =========================
% PARTIE 5 : MOYENNES + STD
%% =========================
intra_q = zeros(3,1);
inter_q = zeros(3,1);

intra_SC_q = zeros(3,1);
inter_SC_q = zeros(3,1);

std_intra_q = zeros(3,1);
std_inter_q = zeros(3,1);

std_intra_SC_q = zeros(3,1);
std_inter_SC_q = zeros(3,1);

age_q = zeros(3,1);

fprintf('\nConnectivité par quartile\n\n')

for k = 1:3
    
    idx = find(groups == k);
    
    age_q(k) = mean(ages(idx));
    
    % FC
    intra_q(k) = mean(intra_all(idx));
    inter_q(k) = mean(inter_all(idx));
    
    std_intra_q(k) = std(intra_all(idx));
    std_inter_q(k) = std(inter_all(idx));
    
    % SC
    intra_SC_q(k) = mean(intra_SC_all(idx));
    inter_SC_q(k) = mean(inter_SC_all(idx));
    
    std_intra_SC_q(k) = std(intra_SC_all(idx));
    std_inter_SC_q(k) = std(inter_SC_all(idx));
    
    fprintf(['Quartile %d → Age: %.2f | FC Intra: %.3f | FC Inter: %.3f | ' ...
             'SC Intra: %.3f | SC Inter: %.3f\n'], ...
        k, age_q(k), ...
        intra_q(k), inter_q(k), ...
        intra_SC_q(k), inter_SC_q(k));
    
end


%% =========================
% FIGURE FC + BARRES ERREUR
%% =========================
figure;
hold on;

errorbar(age_q, intra_q, 2*std_intra_q, '-o', 'LineWidth', 2);
errorbar(age_q, inter_q, 2*std_inter_q, '--o', 'LineWidth', 2);

xlabel('Âge moyen');
ylabel('Connectivité Fonctionnelle');
title('FC vs âge (par quartile)');

legend('FC Intra','FC Inter');
grid on;


%% =========================
% FIGURE SC (LOG) + ERREURS
%% =========================

% Passage au log
intra_SC_q_log = log(intra_SC_q);
inter_SC_q_log = log(inter_SC_q);

% Approximation propagation erreur
std_intra_SC_log = std_intra_SC_q ./ intra_SC_q;
std_inter_SC_log = std_inter_SC_q ./ inter_SC_q;

figure;
hold on;

errorbar(age_q, intra_SC_q_log, 2*std_intra_SC_log, '-s', 'LineWidth', 2);
errorbar(age_q, inter_SC_q_log, 2*std_inter_SC_log, '--s', 'LineWidth', 2);

xlabel('Âge moyen');
ylabel('SC (log)');
title('SC log vs âge (par quartile)');

legend('SC Intra','SC Inter');
grid on;

%% ============
% CODE 2
%% ============

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

%% ===================================
% Modularité / Allégance / Correlation
%% ===================================

%% ========================================================================
%  PARAMÈTRES GLOBAUX
%% ========================================================================
gamma   = 1;
n_runs  = 100;
tau     = 0.5;
reps    = 50;
N       = length(ages);
N_nodes = size(SUBJECT_1.FC, 1);

% Initialisation des métriques de réseau
Q_FC     = zeros(N,1);
Ci_FC    = zeros(N, N_nodes);
intra_FC = zeros(N, 1);
inter_FC = zeros(N, 1);

Q_SC     = zeros(N,1);
Ci_SC    = zeros(N, N_nodes);
intra_SC = zeros(N, 1);
inter_SC = zeros(N, 1);

%% ========================================================================
%  ANALYSE FC : CONSENSUS + INTRA/INTER
%% ========================================================================
fprintf('Analyse FC pour %d sujets...\n', N);
for i = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    FC = SUBJECT.FC;
    FC(1:N_nodes+1:end) = 0; % Enlever diagonale
    
    Ci_runs = zeros(n_runs, N_nodes);
    Q_runs  = zeros(n_runs, 1);
    
    for r = 1:n_runs
        [Ci, Q] = community_louvain(FC, gamma, [], 'negative_sym');
        Ci_runs(r,:) = Ci;
        Q_runs(r) = Q;
    end
    
    % CONSENSUS
    D = agreement(Ci_runs');
    Ci_consensus = consensus_und(D, tau, reps);
    Ci_FC(i,:) = Ci_consensus;
    Q_FC(i)    = mean(Q_runs);
    
    % --- CALCUL INTRA/INTER FC ---
    mask_intra = (Ci_consensus == Ci_consensus');
    mask_intra(logical(eye(N_nodes))) = 0; % Retirer diagonale
    mask_inter = ~mask_intra;
    mask_inter(logical(eye(N_nodes))) = 0;
    
    intra_FC(i) = mean(FC(mask_intra));
    inter_FC(i) = mean(FC(mask_inter));
    
    % Affichage debug pour le sujet 1 (Version affinée)
    if i == 1
        figure('Name', 'FC : Partitions vs Consensus');
        
        % Subplot 1 : Les 100 runs Louvain
        subplot(4,1,1:3) 
        imagesc(Ci_runs)
        title('FC - Partitions de tous les runs')
        ylabel('Runs')
        set(gca, 'XTick', []) % Cache l'axe X pour coller au plot du bas
        colorbar
        
        % Subplot 2 : Le consensus (Ligne fine)
        subplot(4,1,4)
        imagesc(Ci_consensus') 
        title('FC - Partition Consensus')
        set(gca, 'YTick', [], 'YColor', 'none') % Supprime l'aspect étiré
        xlabel('Nœuds')
        colorbar
    end
end

%% ========================================================================
%  ANALYSE SC : CONSENSUS + INTRA/INTER
%% ========================================================================
fprintf('Analyse SC pour %d sujets...\n', N);
for i = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    SC = SUBJECT.SC;
    SC(1:N_nodes+1:end) = 0;
    W = log(SC + 1); % Utilisation du Log-SC pour la modularité
    
    Ci_runs = zeros(n_runs, N_nodes);
    Q_runs  = zeros(n_runs, 1);
    
    for r = 1:n_runs
        [Ci, Q] = community_louvain(W, gamma);
        Ci_runs(r,:) = Ci;
        Q_runs(r) = Q;
    end
    
    % CONSENSUS
    D = agreement(Ci_runs');
    Ci_consensus = consensus_und(D, tau, reps);
    Ci_SC(i,:) = Ci_consensus;
    Q_SC(i)    = mean(Q_runs);
    
    % --- CALCUL INTRA/INTER SC ---
    mask_intra_s = (Ci_consensus == Ci_consensus');
    mask_intra_s(logical(eye(N_nodes))) = 0;
    mask_inter_s = ~mask_intra_s;
    mask_inter_s(logical(eye(N_nodes))) = 0;
    
    intra_SC(i) = mean(W(mask_intra_s));
    inter_SC(i) = mean(W(mask_inter_s));
    
    % Affichage debug pour le sujet 1 (Version affinée)
    if i == 1
        figure('Name', 'SC : Partitions vs Consensus');
        subplot(4,1,1:3)
        imagesc(Ci_runs)
        title('SC (Log) - Partitions de tous les runs')
        ylabel('Runs'); set(gca, 'XTick', []); colorbar;
        
        subplot(4,1,4)
        imagesc(Ci_consensus')
        title('SC (Log) - Partition Consensus')
        set(gca, 'YTick', [], 'YColor', 'none')
        xlabel('Nœuds'); colorbar;
    end
end

%% ========================================================================
%  ANALYSE DE LA SÉGRÉGATION (EFFET DE L'ÂGE)
%% ========================================================================
% L'index de ségrégation mesure à quel point les modules sont isolés
seg_FC = (intra_FC - inter_FC) ./ intra_FC;
seg_SC = (intra_SC - inter_SC) ./ intra_SC;

figure('Name', 'Analyse Intra/Inter Modulaire');
% Graphique FC
subplot(1,2,1);
scatter(ages, seg_FC, 'filled', 'MarkerFaceAlpha', 0.6);
hold on;
mdl_f = fitlm(ages, seg_FC);
plot(ages, mdl_f.Fitted, 'r', 'LineWidth', 2);
title(sprintf('Ségrégation FC (p=%.3f)', mdl_f.Coefficients.pValue(2)));
xlabel('Âge'); ylabel('Index de Ségrégation'); grid on;

% Graphique SC
subplot(1,2,2);
scatter(ages, seg_SC, 'filled', 'MarkerFaceColor', [0.2 0.6 0.2], 'MarkerFaceAlpha', 0.6);
hold on;
mdl_s = fitlm(ages, seg_SC);
plot(ages, mdl_s.Fitted, 'r', 'LineWidth', 2);
title(sprintf('Ségrégation SC (p=%.3f)', mdl_s.Coefficients.pValue(2)));
xlabel('Âge'); grid on;

%% ========================================================================
%  ANALYSE MULTIMODALE (ALLÉGEANCE) SUR SUBJECT_1
%% ========================================================================
SUBJECT = SUBJECT_1; 
FC = SUBJECT.FC; FC(1:N_nodes+1:end) = 0;
SC = SUBJECT.SC; SC(1:N_nodes+1:end) = 0;
SC_log = log(SC + 1);

modes = {'FC', 'SC', 'Log-SC'};
data_cell = {FC, SC, SC_log};

for m = 1:length(modes)
    current_data = data_cell{m};
    fprintf('\n--- Allégeance : %s ---\n', modes{m});
    
    Ci_runs = zeros(n_runs, N_nodes);
    for r = 1:n_runs
        if strcmp(modes{m}, 'FC')
            [Ci, ~] = community_louvain(current_data, gamma, [], 'negative_sym');
        else
            [Ci, ~] = community_louvain(current_data, gamma);
        end
        Ci_runs(r,:) = Ci;
    end
    
    P = agreement(Ci_runs') / n_runs;
    
    figure('Name', sprintf('Allégeance %s', modes{m}));
    imagesc(P); colorbar; axis square;
    title(sprintf('Probabilité de co-classification (%s)', modes{m}));
    
    % Tri par consensus du sujet 1
    if strcmp(modes{m}, 'FC'), Ci_ref = Ci_FC(1,:)'; else Ci_ref = Ci_SC(1,:)'; end
    [Ci_sorted, idx_nodes] = sort(Ci_ref);
    Mat_sorted = current_data(idx_nodes, idx_nodes);
    
    figure('Name', sprintf('Matrice triée %s', modes{m}));
    imagesc(Mat_sorted); colormap(jet); colorbar; axis square;
    title(sprintf('Matrice %s réordonnée par modules', modes{m}));
    
    hold on;
    mod_list = unique(Ci_sorted);
    pos = 0;
    for mod_idx = 1:length(mod_list)
        n_m = sum(Ci_sorted == mod_list(mod_idx));
        pos = pos + n_m;
        line([pos pos],[0 N_nodes],'Color','k','LineWidth',1.5)
        line([0 N_nodes],[pos pos],'Color','k','LineWidth',1.5)
    end
end

%% ==================
% Diagramme de Sankey
%% ==================

%% ==========================================
% PARTIE FC : CALCUL ET EXPORT
% ==========================================
% Consensus par groupe pour FC
D1_FC = agreement(Ci_FC(find(groups==1), :)') / sum(groups==1);
Ci_FC_G1 = consensus_und(D1_FC, tau, reps);

D2_FC = agreement(Ci_FC(find(groups==2), :)') / sum(groups==2);
Ci_FC_G2 = consensus_und(D2_FC, tau, reps);

D3_FC = agreement(Ci_FC(find(groups==3), :)') / sum(groups==3);
Ci_FC_G3 = consensus_und(D3_FC, tau, reps);

% Export FC
T_FC = table(Ci_FC_G1, Ci_FC_G2, Ci_FC_G3, 'VariableNames', {'G1', 'G2', 'G3'});
writetable(T_FC, 'sankey_data_FC.csv');
fprintf('Fichier sankey_data_FC.csv enregistré !\n');

%% ==========================================
% PARTIE SC : CALCUL ET EXPORT
% ==========================================
% Consensus par groupe pour SC
D1_SC = agreement(Ci_SC(find(groups==1), :)') / sum(groups==1);
Ci_SC_G1 = consensus_und(D1_SC, tau, reps);

D2_SC = agreement(Ci_SC(find(groups==2), :)') / sum(groups==2);
Ci_SC_G2 = consensus_und(D2_SC, tau, reps);

D3_SC = agreement(Ci_SC(find(groups==3), :)') / sum(groups==3);
Ci_SC_G3 = consensus_und(D3_SC, tau, reps);

% Export SC
T_SC = table(Ci_SC_G1, Ci_SC_G2, Ci_SC_G3, 'VariableNames', {'G1', 'G2', 'G3'});
writetable(T_SC, 'sankey_data_SC.csv');
fprintf('Fichier sankey_data_SC.csv enregistré !\n');

%% ========================================================================
%  PARTITIONS MODULAIRES SUR LES MATRICES MOYENNES (PAR GROUPE)
%% ========================================================================
% Paramètres pour Louvain
gamma = 1;
n_runs = 100;
tau = 0.5;
reps = 50;

% Initialisation des matrices de stockage pour les partitions (68 nœuds x 3 groupes)
Ci_FC_mean_groups = zeros(N_nodes, 3);
Ci_SC_mean_groups = zeros(N_nodes, 3);

fprintf('\nCalcul des partitions sur les matrices moyennes...\n');

for k = 1:3
    fprintf('Traitement du Groupe %d...\n', k);
    
    % 1. Extraire les sujets du groupe et calculer la moyenne
    idx = find(groups == k);
    count = length(idx);
    
    sum_FC = zeros(N_nodes, N_nodes);
    sum_SC = zeros(N_nodes, N_nodes);
    
    for i = 1:count
        SUB = eval(sprintf('SUBJECT_%d', idx(i)));
        sum_FC = sum_FC + SUB.FC;
        sum_SC = sum_SC + SUB.SC;
    end
    
    FC_avg = sum_FC / count;
    SC_avg = sum_SC / count;
    
    % Nettoyage diagonale
    FC_avg(1:N_nodes+1:end) = 0;
    SC_avg(1:N_nodes+1:end) = 0;
    W_SC_avg = log(SC_avg + 1); % Utilisation du log pour la modularité SC

    % --- MODULARITÉ FC MOYENNE ---
    Ci_runs_FC = zeros(n_runs, N_nodes);
    for r = 1:n_runs
        [Ci, ~] = community_louvain(FC_avg, gamma, [], 'negative_sym');
        Ci_runs_FC(r,:) = Ci;
    end
    D_FC = agreement(Ci_runs_FC') / n_runs;
    Ci_FC_mean_groups(:,k) = consensus_und(D_FC, tau, reps);

    % --- MODULARITÉ SC MOYENNE ---
    Ci_runs_SC = zeros(n_runs, N_nodes);
    for r = 1:n_runs
        [Ci, ~] = community_louvain(W_SC_avg, gamma);
        Ci_runs_SC(r,:) = Ci;
    end
    D_SC = agreement(Ci_runs_SC') / n_runs;
    Ci_SC_mean_groups(:,k) = consensus_und(D_SC, tau, reps);
end

%% =========================
% VISUALISATION DES PARTITIONS
%% =========================
figure('Name', 'Partitions des Matrices Moyennes');

% Affichage FC
subplot(2,1,1);
imagesc(Ci_FC_mean_groups');
title('Partitions Modulaires : FC Moyenne par Groupe');
set(gca, 'YTick', 1:3, 'YTickLabel', {'G1', 'G2', 'G3'});
ylabel('Groupes d''âge'); colorbar;

% Affichage SC
subplot(2,1,2);
imagesc(Ci_SC_mean_groups');
title('Partitions Modulaires : SC Moyenne par Groupe');
xlabel('Nœuds (ROI)'); 
set(gca, 'YTick', 1:3, 'YTickLabel', {'G1', 'G2', 'G3'});
ylabel('Groupes d''âge'); colorbar;

%% =========================
% EXPORT POUR SANKEY (Optionnel)
%% =========================
T_FC_mean = table(Ci_FC_mean_groups(:,1), Ci_FC_mean_groups(:,2), Ci_FC_mean_groups(:,3), ...
    'VariableNames', {'G1', 'G2', 'G3'});
writetable(T_FC_mean, 'sankey_data_FC_MEANS.csv');

T_SC_mean = table(Ci_SC_mean_groups(:,1), Ci_SC_mean_groups(:,2), Ci_SC_mean_groups(:,3), ...
    'VariableNames', {'G1', 'G2', 'G3'});
writetable(T_SC_mean, 'sankey_data_SC_MEANS.csv');

fprintf('Terminé ! Partitions sauvegardées dans les variables Ci_FC_mean_groups et Ci_SC_mean_groups.\n');

%% ========================================================================
%  CALCUL CLUSTERING ET EFFICIENCY (FC)
%% ========================================================================
C_all = zeros(N, 1);    % Clustering moyen par sujet
E_glob = zeros(N, 1);   % Efficiency globale par sujet
E_loc = zeros(N, 1);    % Efficiency locale par sujet

thr = 0.15; % On garde le même seuil que tout à l'heure

for i = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    W = SUBJECT.FC;
    W(1:N_nodes+1:end) = 0;
    W(W < 0) = 0; % On ignore les négatifs pour ces métriques standards
    
    % On applique le seuil
    W_thr = threshold_proportional(W, thr);
    
    % 1. Clustering Coefficient (retourne un vecteur de 68 nœuds, on prend la moyenne)
    C_vec = clustering_coef_wu(W_thr);
    C_all(i) = mean(C_vec);
    
    % 2. Global Efficiency (Scolaire, retourne une valeur unique)
    E_glob(i) = efficiency_wei(W_thr);
    
    % 3. Local Efficiency (retourne un vecteur, on prend la moyenne)
    % Le '2' indique qu'on veut l'efficience locale
    E_loc_vec = efficiency_wei(W_thr, 2);
    E_loc(i) = mean(E_loc_vec);
end

% Tu peux maintenant utiliser tes fonctions de graphiques (G1, G2, G3) 
% pour voir comment E_glob et C_all varient avec l'âge.

%% ========================================================================
%  STATISTIQUES PAR GROUPE : EFFICIENCY ET CLUSTERING
%% ========================================================================
% Initialisation des vecteurs pour les moyennes et erreurs
mean_E = zeros(3,1); sem_E = zeros(3,1);
mean_C = zeros(3,1); sem_C = zeros(3,1);

for k = 1:3
    idx = (groups == k);
    
    % Statistiques pour l'Efficience Globale (Intégration)
    mean_E(k) = mean(E_glob(idx));
    sem_E(k)  = std(E_glob(idx)) / sqrt(sum(idx));
    
    % Statistiques pour le Clustering (Ségrégation locale)
    mean_C(k) = mean(C_all(idx));
    sem_C(k)  = std(C_all(idx)) / sqrt(sum(idx));
end

%% ========================================================================
%  RECALCUL DE LA MODULARITÉ AVEC SEUIL (THRESHOLD) - 3 GROUPES
%% ========================================================================

% Paramètres de l'analyse
threshold_value = 0.15; % On garde les 15% des connexions les plus fortes
gamma = 1;              % Paramètre de résolution Louvain
Q_FC_thr = zeros(N, 1);

fprintf('Application du seuil (%.0f%%) et calcul de Q...\n', threshold_value*100);

for i = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    FC = SUBJECT.FC;
    
    % 1. Nettoyage de la matrice
    FC(1:N_nodes+1:end) = 0; % Enlever diagonale
    FC(isnan(FC)) = 0;       % Enlever NaNs
    FC(FC < 0) = 0;          % On ne garde que les valeurs positives pour le seuillage
    
    % 2. Application du seuil proportionnel (BCT)
    % Cette fonction garde les X% de liens les plus forts
    FC_thresholded = threshold_proportional(FC, threshold_value);
    
    % 3. Calcul de la modularité sur la matrice seuillée
    [~, Q_tmp] = community_louvain(FC_thresholded, gamma);
    Q_FC_thr(i) = Q_tmp;
end

%% ========================================================================
%  MOYENNAGE PAR GROUPE ET VISUALISATION
%% ========================================================================

mean_Q_thr = zeros(3,1);
sem_Q_thr  = zeros(3,1); % Erreur Standard
mean_age_groups = zeros(3,1);

for k = 1:3
    idx = (groups == k);
    mean_Q_thr(k) = mean(Q_FC_thr(idx));
    sem_Q_thr(k)  = std(Q_FC_thr(idx)) / sqrt(sum(idx));
    mean_age_groups(k) = mean(ages(idx));
end

% Création du graphique
figure('Name', 'Modularité Seuillée vs Âge', 'Color', 'k');
hold on;

% Ligne de tendance
plot(mean_age_groups, mean_Q_thr, '--', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.5);

% Points avec barres d'erreur
errorbar(mean_age_groups, mean_Q_thr, sem_Q_thr, '-o', ...
    'LineWidth', 2.5, 'MarkerSize', 10, ...
    'MarkerFaceColor', [0.85 0.33 0.1], 'Color', [0.85 0.33 0.1], 'CapSize', 10);

grid on;
set(gca, 'FontSize', 12, 'LineWidth', 1.2);
xlabel('Âge moyen du groupe (ans)', 'FontSize', 14);
ylabel(['Modularité Moyenne (Q) - Seuil ' num2str(threshold_value*100) '%'], 'FontSize', 14);
title(['Évolution de la Modularité (FC) avec Seuil de ' num2str(threshold_value*100) '%'], 'FontSize', 16);

% Ajustement des axes pour la lisibilité
xlim([min(ages)-5, max(ages)+5]);

%% ========================================================================
%  CALCUL CLUSTERING ET EFFICIENCY (SC) - AJOUT
%% ========================================================================
C_SC_all = zeros(N, 1);    
E_SC_glob = zeros(N, 1);   

fprintf('Calcul des métriques structurales (SC) pour %d sujets...\n', N);

for i = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    % On travaille sur la matrice structurale
    W_SC = SUBJECT.SC;
    W_SC(1:N_nodes+1:end) = 0;
    
    % Pour la SC, on utilise souvent le log pour compresser les ordres de grandeur
    % et on normalise pour que les poids soient entre 0 et 1 (requis pour certaines fonctions BCT)
    W_SC_log = log(W_SC + 1);
    W_SC_norm = W_SC_log / max(W_SC_log(:)); 
    
    % 1. Clustering Coefficient SC
    C_vec_SC = clustering_coef_wu(W_SC_norm);
    C_SC_all(i) = mean(C_vec_SC);
    
    % 2. Global Efficiency SC
    E_SC_glob(i) = efficiency_wei(W_SC_norm);
end

% Calcul des statistiques par groupe pour la SC
mean_E_SC = zeros(3,1); sem_E_SC = zeros(3,1);
mean_C_SC = zeros(3,1); sem_C_SC = zeros(3,1);

for k = 1:3
    idx = (groups == k);
    mean_E_SC(k) = mean(E_SC_glob(idx));
    sem_E_SC(k)  = std(E_SC_glob(idx)) / sqrt(sum(idx));
    
    mean_C_SC(k) = mean(C_SC_all(idx));
    sem_C_SC(k)  = std(C_SC_all(idx)) / sqrt(sum(idx));
end

%% ========================================================================
%  AFFICHAGE DU GRAPHIQUE COMPARAISON MULTIMODALE (FC vs SC)
%% ========================================================================
figure('Name', 'Topologie Comparée : FC vs SC', 'Color', 'k');

% --- SUBPLOT 1 : Global Efficiency (Intégration) ---
subplot(1,2,1); hold on;
% Courbe FC
errorbar(age_q, mean_E, sem_E, '-o', 'LineWidth', 2.5, 'MarkerSize', 8, ...
    'MarkerFaceColor', [0.8 0.2 0.2], 'Color', [0.8 0.2 0.2], 'CapSize', 10, ...
    'DisplayName', 'FC');
% Courbe SC
errorbar(age_q, mean_E_SC, sem_E_SC, '-s', 'LineWidth', 2.5, 'MarkerSize', 8, ...
    'MarkerFaceColor', [0.2 0.5 0.8], 'Color', [0.2 0.5 0.8], 'CapSize', 10, ...
    'DisplayName', 'SC');

grid on;
title('Efficience Globale (Intégration)');
xlabel('Âge moyen du groupe');
ylabel('Global Efficiency (Normalized)');
legend('Location', 'northeast', 'TextColor', 'w', 'FontSize', 9);
set(gca, 'FontSize', 11, 'Color', 'k', 'XColor', 'w', 'YColor', 'w');

% --- SUBPLOT 2 : Clustering Coefficient (Ségrégation locale) ---
subplot(1,2,2); hold on;
% Courbe FC
errorbar(age_q, mean_C, sem_C, '-o', 'LineWidth', 2.5, 'MarkerSize', 8, ...
    'MarkerFaceColor', [0.2 0.6 0.2], 'Color', [0.2 0.6 0.2], 'CapSize', 10, ...
    'DisplayName', 'FC');
% Courbe SC
errorbar(age_q, mean_C_SC, sem_C_SC, '-s', 'LineWidth', 2.5, 'MarkerSize', 8, ...
    'MarkerFaceColor', [0.9 0.6 0.1], 'Color', [0.9 0.6 0.1], 'CapSize', 10, ...
    'DisplayName', 'SC');

grid on;
title('Coefficient de Clustering (Ségrégation locale)');
xlabel('Âge moyen du groupe');
ylabel('Mean Clustering Coefficient');
legend('Location', 'northeast', 'TextColor', 'w', 'FontSize', 9);
set(gca, 'FontSize', 11, 'Color', 'k', 'XColor', 'w', 'YColor', 'w');

% Titre global
sgtitle('Évolution Structure-Fonction avec l''âge (3 groupes)', 'FontSize', 14, 'Color', 'w');

%% ========================================================================
%  ANALYSE PAR MODÈLE NUL (NULL NETWORK MODELS)
%% ========================================================================
n_rand = 20; % Nombre de randomisations par sujet (100 est l'idéal, mais plus lent)
Q0_all = zeros(N, 1);
Q_norm_all = zeros(N, 1);

fprintf('Calcul des modèles nuls pour %d sujets (%d itérations chacun)...\n', N, n_rand);

for i = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    W = SUBJECT.FC;
    W(1:N_nodes+1:end) = 0;
    W(isnan(W)) = 0;
    
    % On utilise ici la matrice seuillée comme dans votre analyse précédente
    W_thr = threshold_proportional(W, 0.15); 
    
    Q0_runs = zeros(n_rand, 1);
    for r = 1:n_rand
        % Génération du réseau aléatoire (Null Model)
        % null_model_und_sign préserve les distributions de poids et de force
        [W_null, ~] = null_model_und_sign(W_thr);
        
        % Calcul de la modularité du modèle nul (Q0)
        [~, Q0_tmp] = community_louvain(W_null, gamma);
        Q0_runs(r) = Q0_tmp;
    end
    
    % Moyenne de Q0 pour le sujet i
    Q0_all(i) = mean(Q0_runs);
    
    % Calcul de la modularité normalisée : (Q_obs - Q_null) / Q_null
    % Note : Q_FC_thr(i) doit avoir été calculé au préalable
    Q_norm_all(i) = (Q_FC_thr(i) - Q0_all(i)) / Q0_all(i);
end

%% ========================================================================
%  MOYENNAGE ET VISUALISATION PAR GROUPE (G1, G2, G3)
%% ========================================================================
mean_Qnorm_groups = zeros(3,1);
sem_Qnorm_groups  = zeros(3,1);

for k = 1:3
    idx = (groups == k);
    mean_Qnorm_groups(k) = mean(Q_norm_all(idx));
    sem_Qnorm_groups(k)  = std(Q_norm_all(idx)) / sqrt(sum(idx));
end

figure('Name', 'Modularité Normalisée par rapport au Modèle Nul', 'Color', 'k');
errorbar(mean_age_groups, mean_Qnorm_groups, sem_Qnorm_groups, '-o', ...
    'LineWidth', 2, 'MarkerSize', 10, 'MarkerFaceColor', [0.4 0.2 0.6], 'Color', [0.4 0.2 0.6]);

grid on;
xlabel('Âge moyen du groupe');
ylabel('(Q_{obs} - Q_{null}) / Q_{null}');
title('Évolution de la Modularité Normalisée (Excès de modularité)');

%% ========================================================================
%  MOYENNES GLOBALES (FC & SC) - NOUVEL ONGLET STABLE (ORDRE G1)
%% ========================================================================

% 1. Configuration pour que toutes les nouvelles figures soient des onglets
set(0, 'DefaultFigureWindowStyle', 'docked'); 

% 2. Définition des labels
regions_base = {'bankssts', 'caudalanteriorcingulate', 'caudalmiddlefrontal', 'cuneus', ...
    'entorhinal', 'fusiform', 'inferiorparietal', 'inferiortemporal', 'isthmuscingulate', ...
    'lateraloccipital', 'lateralorbitofrontal', 'lingual', 'medialorbitofrontal', ...
    'middletemporal', 'parahippocampal', 'paracentral', 'parsopercularis', 'parsorbitalis', ...
    'parstriangularis', 'pericalcarine', 'postcentral', 'posteriorcingulate', 'precentral', ...
    'precuneus', 'rostralanteriorcingulate', 'rostralmiddlefrontal', 'superiorfrontal', ...
    'superiorparietal', 'superiortemporal', 'supramarginal', 'frontalpole', 'temporalpole', ...
    'transversetemporal', 'insula'};

labels_68 = [cellfun(@(x) ['L-' x], regions_base, 'UniformOutput', false), ...
             cellfun(@(x) ['R-' x], regions_base, 'UniformOutput', false)];

important_idx = [3, 7, 14, 21, 23, 24, 27, 28, 34]; 
important_idx = [important_idx, important_idx + 34]; 

% 3. Calcul des moyennes (Globales et Référence G1)
idx_g1 = find(groups == 1);
sum_FC_all = zeros(68,68); sum_SC_all = zeros(68,68);
sum_FC_g1  = zeros(68,68); sum_SC_g1  = zeros(68,68);

for i = 1:N
    SUB = eval(sprintf('SUBJECT_%d', i));
    sum_FC_all = sum_FC_all + SUB.FC;
    sum_SC_all = sum_SC_all + log(SUB.SC + 1);
    if ismember(i, idx_g1)
        sum_FC_g1 = sum_FC_g1 + SUB.FC;
        sum_SC_g1 = sum_SC_g1 + log(SUB.SC + 1);
    end
end

FC_global = sum_FC_all / N;
SC_global = sum_SC_all / N;
FC_ref_g1 = sum_FC_g1 / length(idx_g1);
SC_ref_g1 = sum_SC_g1 / length(idx_g1);

% --- ÉTAPE CRUCIALE : CRÉER UN NOUVEL ONGLET UNIQUE ---
figure('Name', 'Moyennes Globales (N=49)', 'Color', 'k'); 

modes_data = {FC_global, SC_global};
modes_ref  = {FC_ref_g1, SC_ref_g1};
modes_names = {'FC', 'Log-SC'};

for m = 1:2

    current_mat = modes_data{m};
    ref_mat = modes_ref{m};
    ref_mat(1:69:end) = 0;

    % =====================================================
    % DETECTION MODULAIRE ROBUSTE
    % =====================================================

    gamma_mod = 1.3;
    n_runs_mod = 200;

    Ci_runs = zeros(n_runs_mod,68);

    for r = 1:n_runs_mod

        if m == 1
            [Ci_tmp,~] = community_louvain(ref_mat,gamma_mod,[],'negative_sym');
        else
            [Ci_tmp,~] = community_louvain(ref_mat,gamma_mod);
        end

        Ci_runs(r,:) = Ci_tmp;

    end

    D = agreement(Ci_runs');
    Ci_ref = consensus_und(D,0.5,50);

    [Ci_sorted, idx_nodes] = sort(Ci_ref);

    % Labels ordonnés
    Labels_sorted = labels_68(idx_nodes);
    
    [~, loc_in_sorted] = ismember(labels_68(important_idx), Labels_sorted);
    [loc_ordered, ~] = sort(loc_in_sorted);
    
    labels_to_show = Labels_sorted(loc_ordered);

    if m == 1
        clim_vals = [-0.2 0.8];
    else
        clim_vals = [0 max(current_mat(:))*0.9];
    end

    subplot(1,2,m)

    Mat_plot = current_mat(idx_nodes,idx_nodes);
    Mat_plot(1:69:end) = 0;

    imagesc(Mat_plot);
    colormap(jet); 
    colorbar; 
    axis square;
    clim(clim_vals);
    
    title([modes_names{m} ' Moyenne Globale'], 'Color', 'w');
    
    set(gca, 'XTick', loc_ordered, 'XTickLabel', labels_to_show, ...
             'YTick', loc_ordered, 'YTickLabel', labels_to_show, ...
             'TickLabelInterpreter', 'none', ...
             'FontSize', 7, ...
             'XColor', 'w', ...
             'YColor', 'w');
    
    xtickangle(45);

    % Bordures des modules
    hold on
    
    pos = 0;
    mod_list = unique(Ci_sorted);
    
    for mod_idx = 1:length(mod_list)
    
        n_m = sum(Ci_sorted == mod_list(mod_idx));
        pos = pos + n_m;
    
        line([pos+0.5 pos+0.5],[0.5 68.5], ...
            'Color','w','LineWidth',1,'LineStyle',':');
    
        line([0.5 68.5],[pos+0.5 pos+0.5], ...
            'Color','w','LineWidth',1,'LineStyle',':');
    end
end

sgtitle('Synthèse Globale - Organisation Invariante G1','Color','w','FontSize',14);

%% ========================================================================
%  CONFIGURATION GLOBALE DES FIGURES (DOCKING)
%% ========================================================================
% Force toutes les nouvelles figures à s'ouvrir comme des onglets
set(0, 'DefaultFigureWindowStyle', 'docked');

%% ========================================================================
%  ANALYSE DU COUPLAGE STRUCTURE-FONCTION (SC-FC COUPLING)
%% ========================================================================
coupling_all = zeros(N, 1);
fprintf('Calcul du couplage SC-FC pour %d sujets...\n', N);

for i = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    FC = SUBJECT.FC;
    SC = SUBJECT.SC;
    
    % Nettoyage et vectorisation
    FC(logical(eye(N_nodes))) = 0;
    SC(logical(eye(N_nodes))) = 0;
    mask = triu(true(N_nodes), 1);
    
    vec_FC = FC(mask);
    vec_SC = log(SC(mask) + 1); 
    
    % Corrélation sur les liens structurels existants
    idx_present = vec_SC > 0;
    if any(idx_present)
        coupling_all(i) = corr(vec_SC(idx_present), vec_FC(idx_present), 'Type', 'Pearson');
    else
        coupling_all(i) = 0;
    end
end

% Statistiques par groupe
mean_coupling = zeros(3,1);
sem_coupling  = zeros(3,1);
for k = 1:3
    idx = (groups == k);
    mean_coupling(k) = mean(coupling_all(idx));
    sem_coupling(k)  = std(coupling_all(idx)) / sqrt(sum(idx));
end

% --- FIGURE : COUPLAGE (Onglet 22) ---
% Note : On retire 'Position' pour garantir le docking
figure('Name', 'Couplage SC-FC vs Âge', 'Color', 'k');
hold on;
plot(age_q, mean_coupling, '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 1);
errorbar(age_q, mean_coupling, sem_coupling, '-o', ...
    'LineWidth', 2.5, 'MarkerSize', 12, ...
    'MarkerFaceColor', [0.1 0.8 0.3], 'Color', [0.1 0.8 0.3], 'CapSize', 10);
grid on;
set(gca, 'FontSize', 12, 'XColor', 'w', 'YColor', 'w', 'Color', 'k', 'LineWidth', 1.2);
xlabel('Âge moyen du groupe (ans)', 'Color', 'w');
ylabel('Couplage SC-FC (r)', 'Color', 'w');
title('Évolution du Couplage Structure-Fonction', 'Color', 'w');
xlim([min(ages)-5, max(ages)+5]);

%% ========================================================================
%  IDENTIFICATION DES HUBS (COEFFICIENT DE PARTICIPATION)
%% ========================================================================
PC_all = zeros(N, N_nodes);
thr = 0.15;

fprintf('Calcul des Hubs pour %d sujets...\n', N);
for i = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    W = SUBJECT.FC;
    W(1:69:end) = 0;
    W(W < 0) = 0; 
    
    W_thr = threshold_proportional(W, thr);
    Ci = Ci_FC(i,:)'; 
    PC_all(i, :) = participation_coef(W_thr, Ci);
end

% --- FIGURE : HUBS CONNECTEURS (Onglet 23) ---
% Note : On retire également 'Position' ici
figure('Name', 'Identification des Hubs Connecteurs', 'Color', 'k');
mean_PC_groups = zeros(3, N_nodes);

for k = 1:3
    idx = (groups == k);
    mean_PC_groups(k, :) = mean(PC_all(idx, :), 1);
    
    [sorted_val, sorted_idx] = sort(mean_PC_groups(k, :), 'descend');
    top_n = 10;
    top_val = sorted_val(1:top_n);
    top_labels = labels_68(sorted_idx(1:top_n));
    
    subplot(1, 3, k);
    b = barh(1:top_n, top_val, 'FaceColor', [0.9 0.4 0.1]);
    
    set(gca, 'YDir', 'reverse', 'YTick', 1:top_n, 'YTickLabel', top_labels, ...
             'XColor', 'w', 'YColor', 'w', 'Color', 'k', 'FontSize', 9);
    
    xlabel('Participation Coef', 'Color', 'w');
    title(['Top Hubs - Groupe ' num2str(k)], 'Color', 'w');
    grid on; xlim([0 0.8]);
end
sgtitle('Évolution des Hubs d''Intégration (PC) avec l''âge FC', 'Color', 'w', 'FontSize', 16);

%% ========================================================================
%  IDENTIFICATION DES HUBS (STRENGTH CENTRALITY)
%% ========================================================================
% 1. Calcul de la Force (Strength) pour chaque sujet
% Note : On utilise la matrice FC pondérée (weighted)
strength_all = zeros(N, N_nodes);

for i = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    W = SUBJECT.FC;
    W(1:69:end) = 0; % Enlever la diagonale
    W(W < 0) = 0;    % On ne garde que les poids positifs pour la force standard
    
    % La force est la somme des poids des connexions pour chaque nœud
    strength_all(i, :) = sum(W, 2);
end

% 2. Moyennage par groupe d'âge
mean_strength_groups = zeros(3, N_nodes);
for k = 1:3
    idx = (groups == k);
    mean_strength_groups(k, :) = mean(strength_all(idx, :), 1);
end

% 3. VISUALISATION DES TOP HUBS (Onglet dédié)
figure('Name', 'Identification des Hubs (Strength)', 'Color', 'k');

% Couleurs pour différencier de l'analyse PC (un dégradé de bleu/cyan par exemple)
hub_colors = [0.1 0.7 0.8]; 

for k = 1:3
    % Tri des 10 plus grandes forces
    [sorted_val, sorted_idx] = sort(mean_strength_groups(k, :), 'descend');
    top_n = 10;
    top_val = sorted_val(1:top_n);
    top_labels = labels_68(sorted_idx(1:top_n));
    
    subplot(1, 3, k);
    b = barh(1:top_n, top_val, 'FaceColor', hub_colors);
    
    % Inversion de l'axe Y pour avoir le plus gros hub en haut
    set(gca, 'YDir', 'reverse', 'YTick', 1:top_n, 'YTickLabel', top_labels, ...
             'XColor', 'w', 'YColor', 'w', 'Color', 'k', 'FontSize', 9);
    
    xlabel('Strength (Somme des poids)', 'Color', 'w');
    title(['Top Hubs (Strength) - G' num2str(k)], 'Color', 'w');
    grid on; 
    
    % Fixer la limite X pour comparer les groupes entre eux
    xlim([0 max(mean_strength_groups(:))*1.1]);
end

sgtitle('Évolution des Hubs de Connectivité (Strength Centrality) FC', 'Color', 'w', 'FontSize', 16);

%% ========================================================================
%  ANALYSE DE LA DISTANCE DE CONNECTIVITÉ (AVEC BARRES D'ERREUR)
%% ========================================================================

% 1. Coordonnées MNI (inchangées)
coords_68 = [
    -51, -43, 8; -4, 25, 24; -34, 19, 44; -7, -78, 20; -24, -14, -36; -30, -38, -19;
    -42, -67, 34; -48, -25, -28; -8, -48, 16; -40, -82, 11; -31, 26, -14; -15, -67, -4;
    -5, 41, -15; -54, -20, -14; -22, -30, -15; -7, -32, 57; -44, 15, 22; -40, 31, -11;
    -46, 26, 9; -10, -83, 3; -43, -18, 48; -7, -27, 40; -41, -11, 46; -8, -55, 52;
    -4, 39, 4; -31, 46, 17; -17, 33, 46; -22, -60, 58; -53, -22, 6; -51, -34, 30;
    -7, 54, -9; -29, 13, -34; -43, -16, 7; -35, 3, 3; % HG
    51, -43, 8; 4, 25, 24; 34, 19, 44; 7, -78, 20; 24, -14, -36; 30, -38, -19;
    42, -67, 34; 48, -25, -28; 8, -48, 16; 40, -82, 11; 31, 26, -14; 15, -67, -4;
    5, 41, -15; 54, -20, -14; 22, -30, -15; 7, -32, 57; 44, 15, 22; 40, 31, -11;
    46, 26, 9; 10, -83, 3; 43, -18, 48; 7, -27, 40; 41, -11, 46; 8, -55, 52;
    4, 39, 4; 31, 46, 17; 17, 33, 46; 22, -60, 58; 53, -22, 6; 51, -34, 30;
    7, 54, -9; 29, 13, -34; 43, -16, 7; 35, 3, 3  % HD
];

% 2. Calcul de la matrice de distance (inchangé)
dist_mat = zeros(68,68);
for i = 1:68
    for j = 1:68
        dist_mat(i,j) = sqrt(sum((coords_68(i,:) - coords_68(j,:)).^2));
    end
end

% 3. Paramètres de binning
dist_bins = 0:20:160;
n_bins = length(dist_bins)-1;
bin_centers = dist_bins(1:end-1) + 10;

% Initialisation des résultats
decay_FC = zeros(3, n_bins);
sem_FC   = zeros(3, n_bins); % Pour stocker l'erreur standard

fprintf('Analyse de la distance et calcul des erreurs...\n');

for k = 1:3
    idx_sub = find(groups == k);
    n_subs = length(idx_sub);
    
    % Matrice temporaire pour stocker la FC moyenne de chaque sujet par tranche
    % (n_sujets_du_groupe x n_tranches)
    sub_bin_means = zeros(n_subs, n_bins);
    
    for i = 1:n_subs
        SUBJECT = eval(sprintf('SUBJECT_%d', idx_sub(i)));
        FC = SUBJECT.FC;
        FC(1:69:end) = 0; % Nettoyage diagonale
        
        mask = triu(true(68), 1);
        v_dist = dist_mat(mask);
        v_FC = FC(mask);
        
        for b = 1:n_bins
            idx_bin = (v_dist >= dist_bins(b) & v_dist < dist_bins(b+1));
            if any(idx_bin)
                sub_bin_means(i, b) = mean(v_FC(idx_bin));
            else
                sub_bin_means(i, b) = NaN;
            end
        end
    end
    
    % Moyenne du groupe
    decay_FC(k, :) = mean(sub_bin_means, 1, 'omitnan');
    % Erreur Standard (SEM) = SD / sqrt(N)
    sem_FC(k, :)   = std(sub_bin_means, 0, 1, 'omitnan') ./ sqrt(n_subs);
end

% 4. VISUALISATION
set(0, 'DefaultFigureWindowStyle', 'docked');
figure('Name', 'Décroissance de la Connectivité avec la Distance', 'Color', 'k');
hold on;
colors = [0.2 0.6 1; 1 0.6 0.2; 0.8 0.2 0.2]; % Bleu, Orange, Rouge

for k = 1:3
    % Remplacement de plot par errorbar
    errorbar(bin_centers, decay_FC(k,:), sem_FC(k,:), '-o', ...
        'Color', colors(k,:), ...
        'LineWidth', 2.5, ...
        'MarkerSize', 8, ...
        'MarkerFaceColor', colors(k,:), ...
        'CapSize', 10); % Taille des barres horizontales aux extrémités
end

grid on;
set(gca, 'XColor', 'w', 'YColor', 'w', 'Color', 'k', 'FontSize', 11, 'GridColor', [0.3 0.3 0.3]);
xlabel('Distance Euclidienne (mm)', 'Color', 'w', 'FontSize', 12);
ylabel('Force de Connectivité moyenne (FC)', 'Color', 'w', 'FontSize', 12);
title('Décroissance de la FC en fonction de la Distance (Effet d''âge)', 'Color', 'w', 'FontSize', 14);
legend({'G1 (Jeunes)', 'G2 (Moyens)', 'G3 (Âgés)'}, 'TextColor', 'w', 'Color', 'none', 'EdgeColor', 'w');


%% ========================================================================
%  CARTOGRAPHIE RÉGIONALE DES EFFETS DE L'ÂGE (NODAL ANALYSIS) - CORRIGÉ
%% ========================================================================

% 1. Initialisation
set(0, 'DefaultFigureWindowStyle', 'docked');
betas_age = zeros(N_nodes, 1);  
pvals_age = zeros(N_nodes, 1);  
node_strength_all = zeros(N, N_nodes);

fprintf('Analyse régionale de l''âge sur %d nœuds...\n', N_nodes);

% Calcul de la force (Strength) pour chaque nœud
for i = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    W = SUBJECT.FC;
    W(1:69:end) = 0;
    W(W < 0) = 0; 
    node_strength_all(i, :) = sum(W, 2);
end

% 2. Régression linéaire par nœud : Strength ~ Age
for n = 1:N_nodes
    mdl = fitlm(ages, node_strength_all(:, n));
    
    % --- CORRECTION DES NOMS DE COLONNES ---
    betas_age(n) = mdl.Coefficients.Estimate(2); % La pente (beta)
    pvals_age(n) = mdl.Coefficients.pValue(2);   % La p-valeur (C'était ici l'erreur)
end

% 3. VISUALISATION (Onglet 26)
[sorted_betas, idx_sort] = sort(betas_age, 'ascend'); 
sorted_labels = labels_68(idx_sort);
sorted_pvals = pvals_age(idx_sort);

figure('Name', 'Cartographie de l''Âge par Région', 'Color', 'k');

% --- SUBPLOT 1 : Intensité de l'effet ---
subplot(2, 1, 1);
b = bar(1:N_nodes, sorted_betas, 'FaceColor', 'flat');

for n = 1:N_nodes
    if sorted_pvals(n) < 0.05
        b.CData(n,:) = [0.8 0.2 0.2]; % Rouge pour significatif
    else
        b.CData(n,:) = [0.4 0.4 0.4]; % Gris pour non-significatif
    end
end

grid on;
set(gca, 'XColor', 'w', 'YColor', 'w', 'Color', 'k', 'FontSize', 7, ...
         'XTick', 1:N_nodes, 'XTickLabel', sorted_labels);
xtickangle(90);
ylabel('Coefficient d''âge (\beta)', 'Color', 'w');
title('Sensibilité régionale au vieillissement (Rouge : p < 0.05)', 'Color', 'w');

% --- SUBPLOT 2 : Significativité ---
subplot(2, 1, 2);
log_pvals = -log10(sorted_pvals);
stem(1:N_nodes, log_pvals, 'MarkerFaceColor', [0.2 0.6 1], 'Color', [0.2 0.6 1]);
hold on;
line([0 N_nodes+1], [-log10(0.05) -log10(0.05)], 'Color', 'r', 'LineStyle', '--', 'LineWidth', 1.5);

grid on;
set(gca, 'XColor', 'w', 'YColor', 'w', 'Color', 'k', 'FontSize', 7, ...
         'XTick', 1:N_nodes, 'XTickLabel', sorted_labels);
xtickangle(90);
ylabel('-log10(p-value)', 'Color', 'w');
title('Seuil de significativité statistique', 'Color', 'w');

%% ==========================================================
% RICH CLUB ANALYSIS PAR GROUPE D'AGE
% nécessite Brain Connectivity Toolbox
%% ==========================================================

gamma_null = 10;     % nombre d'itérations pour randomisation
n_rand = 100;        % nombre de réseaux nuls

age_groups = unique(groups);
n_groups = length(age_groups);

figure('Color','k')
hold on

for g = 1:n_groups
    
    idx = find(groups == age_groups(g));
    
    % moyenne des matrices du groupe
    SC_group = zeros(68);
    
    for i = 1:length(idx)
        SUB = eval(sprintf('SUBJECT_%d', idx(i)));
        SC_group = SC_group + log(SUB.SC + 1);
    end
    
    SC_group = SC_group / length(idx);
    
    % supprimer diagonale
    SC_group(1:69:end) = 0;
    
    % --- Rich club coefficient ---
    phi = rich_club_wu(SC_group);
    
    % --- Réseaux nuls ---
    phi_rand = zeros(n_rand,length(phi));
    
    for r = 1:n_rand
        
        W_rand = null_model_und_sign(SC_group,gamma_null);
        
        phi_rand(r,:) = rich_club_wu(W_rand);
        
    end
    
    phi_rand_mean = mean(phi_rand);
    
    % --- Rich club normalisé ---
    phi_norm = phi ./ phi_rand_mean;
    
    plot(phi_norm,'LineWidth',2)
    
end

xlabel('Degré k')
ylabel('Rich Club Normalisé')
legend('Groupe 1','Groupe 2','Groupe 3')
title('Rich Club Organisation par Groupe d''Age SC')

grid on

%% ========================================================================
%  CALCUL DE L'INDEX DE LATÉRALISATION (LI)
%% ========================================================================

% Initialisation
all_LI = zeros(length(groups), 1); % Pour stocker le LI de chaque sujet

for i = 1:length(groups)
    % Récupération de la FC du sujet
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    FC = SUBJECT.FC;
    FC(1:69:end) = 0; % Mise à zéro de la diagonale
    
    % 1. Extraction des blocs de connectivité Intra-Hémisphérique
    % L'atlas Desikan 68 est divisé en : 1-34 (Gauche) et 35-68 (Droite)
    FC_Left  = FC(1:34, 1:34);
    FC_Right = FC(35:68, 35:68);
    
    % 2. Calcul de la force moyenne de chaque côté (en ignorant la diagonale)
    % On ne prend que la partie triangulaire supérieure pour éviter les doublons
    mask_tri = triu(true(34), 1);
    mean_L = mean(FC_Left(mask_tri));
    mean_R = mean(FC_Right(mask_tri));
    
    % 3. Calcul du LI
    all_LI(i) = (mean_L - mean_R) / (mean_L + mean_R);
end

%% 3. VISUALISATION DES RÉSULTATS (Boxplot par Groupe)
figure('Name', 'Index de Latéralisation par Groupe', 'Color', 'k');
hold on;

% 1. Tracer le boxplot
h = boxplot(all_LI, groups, 'Labels', {'G1 (Jeunes)', 'G2 (Moyens)', 'G3 (Âgés)'});

% 2. Définir les couleurs
colors_box = [0.2 0.6 1; 1 0.6 0.2; 0.8 0.2 0.2]; 

% 3. Identifier et colorier les boîtes
obj_boxes = findobj(gca, 'Tag', 'Box');
for j = 1:length(obj_boxes)
    patch(get(obj_boxes(j), 'XData'), ...
          get(obj_boxes(j), 'YData'), ...
          colors_box(end-j+1, :), ... 
          'FaceAlpha', 0.4, ...        
          'EdgeColor', 'none');       
end

% --- AJOUT DES TITRES ET LABELS ---
title('Asymétrie de la Connectivité (Index de Latéralisation)', 'Color', 'w', 'FontSize', 14, 'FontWeight', 'bold');
ylabel('LI : (FC_G - FC_D) / (FC_G + FC_D)', 'Color', 'w', 'FontSize', 12);
xlabel('Groupes d''âge', 'Color', 'w', 'FontSize', 12);

% 5. Esthétique finale
set(h, 'Color', 'w', 'LineWidth', 1.5); 
set(gca, 'Color', 'k', 'XColor', 'w', 'YColor', 'w', 'FontSize', 11);
% Ajuster les limites de l'axe Y pour centrer sur les données
% Un intervalle de [-0.2, 0.2] est généralement idéal pour le LI
ylim([-0.2 0.2]);
grid on;
set(gca, 'GridColor', [0.3 0.3 0.3], 'GridAlpha', 0.5); % Grille discrète
yline(0, '--w', 'LineWidth', 1); % Ligne de référence pour la symétrie parfaite

% Remonter les médianes au premier plan pour qu'elles soient visibles sur les patchs
uistack(findobj(gca, 'Tag', 'Median'), 'top');

fprintf('Moyenne LI par groupe :\n');
for k = 1:3
    fprintf('Groupe %d : %.4f\n', k, mean(all_LI(groups == k)));
end

%% =========================
% PARAMETERS
%% =========================

N = 49;
window = 30;
step = 1;

%% =========================
% GENERATION dFC STREAM
%% =========================

for i = 1:N
    
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    
    TS = SUBJECT.TS;

    dFCstream = TS2dFCstream(TS, window, step);

    SUBJECT.dFCstream = dFCstream;

    eval(sprintf('SUBJECT_%d = SUBJECT;', i));

end

%% =========================
% CALCUL VITESSE dFC
%% =========================

speed_all = zeros(N,1);

for i = 1:N
    
    SUBJECT = eval(sprintf('SUBJECT_%d', i));
    
    dFCstream = SUBJECT.dFCstream;
    
    [typSpeed, Speeds] = dFC_Speeds(dFCstream);
    
    SUBJECT.dFC_speed = typSpeed;
    SUBJECT.dFC_speeds = Speeds;
    
    speed_all(i) = typSpeed;

    eval(sprintf('SUBJECT_%d = SUBJECT;', i));

end

%% =========================
% MATRICE dFC (EXEMPLE SUJET)
%% =========================

SUBJECT = SUBJECT_1;

dFCstream = SUBJECT.dFCstream;

dFC = dFCstream2dFC(dFCstream);

figure
imagesc(dFC)
axis square
colormap(turbo)
colorbar
caxis([0 1])
xlabel('Temps')
ylabel('Temps')
title('Dynamic Functional Connectivity (dFC)')

%% ==========================================
% FCD recurrence matrices for age groups
%% ==========================================

N = 49;     % nombre de sujets
TR = 2;

window = round(20/TR);
step = 1;

ages = zeros(N,1);

FCD_all = {};

%% ==========================================
% COMPUTE FCD FOR EACH SUBJECT
%% ==========================================

for s = 1:N

    SUBJECT = eval(sprintf('SUBJECT_%d',s));

    TS = SUBJECT.TS;
    ages(s) = SUBJECT.age;

    %% dFC stream

    dFCstream = TS2dFCstream(TS,window,step);

    %% FCD matrix

    FCD = dFCstream2dFC(dFCstream);

    FCD_all{s} = FCD;

end

%% ==========================================
% DEFINE AGE GROUPS
%% ==========================================

age_q = quantile(ages,[0 1/3 2/3 1]);

group = zeros(N,1);

for i = 1:N
    
    if ages(i) <= age_q(2)
        group(i) = 1;
        
    elseif ages(i) <= age_q(3)
        group(i) = 2;
        
    else
        group(i) = 3;
    end
    
end

%% ==========================================
% MEAN FCD FOR EACH GROUP
%% ==========================================

FCD_group = cell(3,1);

for g = 1:3
    
    idx = find(group == g);
    
    FCD_sum = 0;
    
    for k = 1:length(idx)
        
        FCD_sum = FCD_sum + FCD_all{idx(k)};
        
    end
    
    FCD_group{g} = FCD_sum / length(idx);
    
end

%% ==========================================
% PLOT RECURRENCE MATRICES
%% ==========================================

figure

titles = {'Young','Middle Age','Old'}

for g = 1:3
    
    subplot(1,3,g)
    
    imagesc(FCD_group{g})
    
    axis square
    
    colorbar
    
    caxis([0 1])
    
    title(titles{g})
    
    xlabel('Time window')
    ylabel('Time window')
    
end
colormap(turbo)

%% ========================================================================
%  ANALYSE DE LA MÉTA-CONNECTIVITÉ PAR GROUPE D'ÂGE
%% ========================================================================

% Initialisation des noms de groupes pour les titres
group_names = {'Jeunes (G1)', 'Moyens (G2)', 'Seniors (G3)'};
figure('Name', 'Comparaison de la Méta-Connectivité par Groupe', 'Color', 'k', 'Units', 'normalized', 'Position', [0.05 0.2 0.9 0.5]);

for k = 1:3
    % 1. Identification des sujets du groupe k
    idx_group = find(groups == k);
    n_subs = length(idx_group);
    
    % Initialisation de la matrice MC moyenne pour le groupe
    % On récupère la taille d'une MC type (2278 x 2278 pour 68 ROIs)
    SUB_temp = eval(sprintf('SUBJECT_%d', idx_group(1)));
    MC_example = dFCstream2MC(SUB_temp.dFCstream);
    [dim_mc, ~] = size(MC_example);
    
    MC_group_sum = zeros(dim_mc, dim_mc);
    
    fprintf('Calcul de la Méta-Connectivité pour le Groupe %d (%d sujets)...\n', k, n_subs);
    
    % 2. Boucle sur les sujets du groupe
    for i = 1:n_subs
        SUB = eval(sprintf('SUBJECT_%d', idx_group(i)));
        
        % Calcul de la MC individuelle
        MC_sub = dFCstream2MC(SUB.dFCstream);
        
        % Accumulation (on somme pour faire la moyenne plus tard)
        MC_group_sum = MC_group_sum + MC_sub;
    end
    
    % 3. Calcul de la moyenne du groupe
    MC_group_avg = MC_group_sum / n_subs;
    
    % 4. Affichage (Subplot pour comparer les 3 groupes)
    subplot(1, 3, k);
    imagesc(MC_group_avg);
    axis square;
    colormap(turbo);
    colorbar;
    caxis([0 0.5]); % Ajusté car la moyenne est souvent plus basse que 1
    
    set(gca, 'Color', 'k', 'XColor', 'w', 'YColor', 'w', 'FontSize', 9);
    xlabel('Connexions', 'Color', 'w');
    ylabel('Connexions', 'Color', 'w');
    title(group_names{k}, 'Color', 'w', 'FontSize', 12);
end

sgtitle('Évolution de la Méta-Connectivité avec l''âge', 'Color', 'w', 'FontSize', 16);

%% =========================
% META CONNECTIVITY
%% =========================

MC = dFCstream2MC(dFCstream);

figure
imagesc(MC)
axis square
colormap(turbo)
colorbar
caxis([0 1])
xlabel('Connexions')
ylabel('Connexions')
title('Meta-connectivity')

%% =========================
% AGE vs dFC SPEED
%% =========================

mdl = fitlm(ages, speed_all);

figure
scatter(ages, speed_all,60,'filled')
hold on
plot(ages, mdl.Fitted,'r','LineWidth',2)

xlabel('Age')
ylabel('dFC Speed')
title('Dynamic FC Speed vs Age')

grid on

%% =========================
% VITESSE PAR GROUPE D'AGE
%% =========================

mean_speed = zeros(3,1);
sem_speed = zeros(3,1);

for k = 1:3
    
    idx = groups == k;
    
    data = speed_all(idx);
    
    mean_speed(k) = mean(data);
    
    sem_speed(k) = std(data)/sqrt(sum(idx));
    
end

figure
errorbar(1:3, mean_speed, sem_speed,'-o','LineWidth',2,'MarkerSize',8)

xticks([1 2 3])
xticklabels({'Young','Middle','Old'})

xlabel('Age group')
ylabel('dFC Speed')

title('dFC Speed by Age Group')

grid on
%% =========================
% CALCUL K-CORE DYNAMIQUE
%% =========================

SUBJECT = SUBJECT_1;

dFCstream = SUBJECT.dFCstream;

% dimensions
nEdges = size(dFCstream,1);
T = size(dFCstream,2);

% retrouver nombre de ROI
nROI = round((1 + sqrt(1 + 8*nEdges))/2);

threshold = 0.3;

kcore_time = zeros(nROI,T);

%% =========================
% CALCUL K-CORE POUR CHAQUE TEMPS
%% =========================

for t = 1:T
    
    % vecteur des connexions
    vec = dFCstream(:,t);
    
    % reconstruire matrice FC
    FC = zeros(nROI);
    
    ind = triu(true(nROI),1);
    FC(ind) = vec;
    
    % symétriser
    FC = FC + FC';
    
    % matrice d'adjacence binaire
    A = FC > threshold;
    
    % supprimer diagonale
    A(1:nROI+1:end) = 0;
    
    % coreness des noeuds
    kcore = kcoreness_centrality_bu(A);
    
    kcore_time(:,t) = kcore;

end


%% =========================
% FIGURE 1 : K-CORE DANS LE TEMPS
%% =========================

figure

imagesc(kcore_time)

colormap(turbo)
colorbar

xlabel('Time window')
ylabel('ROI')

title('Dynamic k-core structure')


%% =========================
% FIGURE 2 : FORCE DU COEUR DU RESEAU
%% =========================

max_kcore = max(kcore_time);

figure

plot(max_kcore,'LineWidth',2)

xlabel('Time window')
ylabel('Max k-core')

title('Network core strength over time')

grid on


%% =========================
% FIGURE 3 : ROI DANS LE COEUR DU RESEAU
%% =========================

core_nodes = zeros(size(kcore_time));

for t = 1:T
    
    thresh = prctile(kcore_time(:,t), 90); % top 10%
    core_nodes(:,t) = kcore_time(:,t) >= thresh;
    
end

figure
imagesc(core_nodes)

colormap(gray)
colorbar

xlabel('Time window')
ylabel('ROI')

title('Nodes belonging to network core (top 10%)')

%% =========================
% FIGURE 4 : MATRICE FC TRIÉE (SANS SEUILLAGE)
%% =========================

t = round(T/2);

vec = dFCstream(:,t);

FC = zeros(nROI);

ind = triu(true(nROI),1);
FC(ind) = vec;

FC = FC + FC';

% =========================
% COMMUNAUTÉS (SUR MATRICE COMPLÈTE)
% =========================
[Ci, ~] = community_louvain(FC, gamma, [], 'negative_sym');

% =========================
% TRI DES NOEUDS
% =========================
[Ci_sorted, idx] = sort(Ci);
FC_sorted = FC(idx, idx);

% =========================
% AFFICHAGE
% =========================
figure

imagesc(FC_sorted)

axis square
colormap(turbo)
colorbar

xlabel('ROI (sorted)')
ylabel('ROI (sorted)')

title('Functional connectivity matrix (sorted, no threshold)')

% =========================
% FRONTIÈRES DES MODULES
% =========================
hold on

modules = unique(Ci_sorted);
pos = 0;

for i = 1:length(modules)
    
    n = sum(Ci_sorted == modules(i));
    pos = pos + n;
    
    line([pos pos], [0 nROI], 'Color', 'k', 'LineWidth', 1.5)
    line([0 nROI], [pos pos], 'Color', 'k', 'LineWidth', 1.5)
    
end

%% ========================================================================
%  ANALYSE DE LA MÉTA-CONNECTIVITÉ PAR GROUPE D'ÂGE
%% ========================================================================

% Initialisation des noms de groupes pour les titres
group_names = {'Jeunes (G1)', 'Moyens (G2)', 'Seniors (G3)'};
figure('Name', 'Comparaison de la Méta-Connectivité par Groupe', 'Color', 'k', 'Units', 'normalized', 'Position', [0.05 0.2 0.9 0.5]);

for k = 1:3
    % 1. Identification des sujets du groupe k
    idx_group = find(groups == k);
    n_subs = length(idx_group);
    
    % Initialisation de la matrice MC moyenne pour le groupe
    % On récupère la taille d'une MC type (2278 x 2278 pour 68 ROIs)
    SUB_temp = eval(sprintf('SUBJECT_%d', idx_group(1)));
    MC_example = dFCstream2MC(SUB_temp.dFCstream);
    [dim_mc, ~] = size(MC_example);
    
    MC_group_sum = zeros(dim_mc, dim_mc);
    
    fprintf('Calcul de la Méta-Connectivité pour le Groupe %d (%d sujets)...\n', k, n_subs);
    
    % 2. Boucle sur les sujets du groupe
    for i = 1:n_subs
        SUB = eval(sprintf('SUBJECT_%d', idx_group(i)));
        
        % Calcul de la MC individuelle
        MC_sub = dFCstream2MC(SUB.dFCstream);
        
        % Accumulation (on somme pour faire la moyenne plus tard)
        MC_group_sum = MC_group_sum + MC_sub;
    end
    
    % 3. Calcul de la moyenne du groupe
    MC_group_avg = MC_group_sum / n_subs;
    
    % 4. Affichage (Subplot pour comparer les 3 groupes)
    subplot(1, 3, k);
    imagesc(MC_group_avg);
    axis square;
    colormap(turbo);
    colorbar;
    caxis([0 0.5]); % Ajusté car la moyenne est souvent plus basse que 1
    
    set(gca, 'Color', 'k', 'XColor', 'w', 'YColor', 'w', 'FontSize', 9);
    xlabel('Connexions', 'Color', 'w');
    ylabel('Connexions', 'Color', 'w');
    title(group_names{k}, 'Color', 'w', 'FontSize', 12);
end

sgtitle('Évolution de la Méta-Connectivité avec l''âge', 'Color', 'w', 'FontSize', 16);

%% ========================================================================
%  DFC ANALYSIS : EMPIRICAL vs SURROGATES (PHASE RAND + SHUFFLED)
%% ========================================================================

TS = SUBJECT.TS; % [T x N]
[T, N] = size(TS);

TR = 2; % ⚠️ à adapter
step = 1;

%% =========================
% 1. SURROGATES
%% =========================

% --- Phase Randomization ---
TS_pr = zeros(T, N);

for i = 1:N
    x = TS(:,i);
    X = fft(x);
    
    mag = abs(X);
    phase = angle(X);
    
    rand_phase = phase;
    rand_phase(2:floor(T/2)) = rand_phase(2:floor(T/2)) + 2*pi*rand(floor(T/2)-1,1);
    rand_phase(end-floor(T/2)+2:end) = -flip(rand_phase(2:floor(T/2)));
    
    X_new = mag .* exp(1i * rand_phase);
    TS_pr(:,i) = real(ifft(X_new));
end

% --- Time Shuffling ---
TS_sh = zeros(T, N);

for i = 1:N
    TS_sh(:,i) = TS(randperm(T), i);
end

%% =========================
% 2. WINDOW RANGES
%% =========================

win_long = round([60 210] / TR);
win_mid  = round([15 60] / TR);

%% =========================
% 3. INITIALISATION
%% =========================

all_speeds = struct();

types = {'emp','pr','sh'};
TS_all = {TS, TS_pr, TS_sh};

%% =========================
% 4. PIPELINE DFC + SPEED
%% =========================

for i = 1:3
    
    current_TS = TS_all{i};
    
    fprintf('\nProcessing %s...\n', types{i});
    
    speeds_long = [];
    speeds_mid  = [];
    
    % ===== LONG WINDOWS =====
    for w = win_long(1):10:win_long(2)
        
        n_win = floor((T - w)/step) + 1;
        dFC = zeros(N*(N-1)/2, n_win);
        
        for k = 1:n_win
            idx = (k-1)*step + (1:w);
            FC = corr(current_TS(idx,:));
            
            ind = triu(true(N),1);
            dFC(:,k) = FC(ind);
        end
        
        % --- SPEED ---
        for t = 1:n_win-1
            c = corr(dFC(:,t), dFC(:,t+1));
            speeds_long(end+1) = 1 - c;
        end
        
    end
    
    % ===== MID WINDOWS =====
    for w = win_mid(1):5:win_mid(2)
        
        n_win = floor((T - w)/step) + 1;
        dFC = zeros(N*(N-1)/2, n_win);
        
        for k = 1:n_win
            idx = (k-1)*step + (1:w);
            FC = corr(current_TS(idx,:));
            
            ind = triu(true(N),1);
            dFC(:,k) = FC(ind);
        end
        
        % --- SPEED ---
        for t = 1:n_win-1
            c = corr(dFC(:,t), dFC(:,t+1));
            speeds_mid(end+1) = 1 - c;
        end
        
    end
    
    all_speeds.(types{i}).long = speeds_long;
    all_speeds.(types{i}).mid  = speeds_mid;
    
end

%% =========================
% 5. KDE PLOTS
%% =========================

figure

% ===== LONG WINDOWS =====
subplot(2,1,1)
hold on

[f,x] = ksdensity(all_speeds.emp.long);
plot(x,f,'b','LineWidth',2)

[f,x] = ksdensity(all_speeds.pr.long);
plot(x,f,'g--','LineWidth',2)

[f,x] = ksdensity(all_speeds.sh.long);
plot(x,f,'r:','LineWidth',2)

title('dFC speed distribution (60–210 s)')
xlabel('dFC speed')
ylabel('Density')

legend('Empirical','Phase randomized','Shuffled')

% ===== MID WINDOWS =====
subplot(2,1,2)
hold on

[f,x] = ksdensity(all_speeds.emp.mid);
plot(x,f,'b','LineWidth',2)

[f,x] = ksdensity(all_speeds.pr.mid);
plot(x,f,'g--','LineWidth',2)

[f,x] = ksdensity(all_speeds.sh.mid);
plot(x,f,'r:','LineWidth',2)

title('dFC speed distribution (15–60 s)')
xlabel('dFC speed')
ylabel('Density')

legend('Empirical','Phase randomized','Shuffled')

%% =========================
% 6. TEST STATISTIQUE (KS)
%% =========================

fprintf('\n===== KS TESTS =====\n')

[h,p] = kstest2(all_speeds.emp.long, all_speeds.pr.long);
fprintf('Emp vs Phase (long): p = %.10e\n', p);

[h,p] = kstest2(all_speeds.emp.long, all_speeds.sh.long);
fprintf('Emp vs Shuffled (long): p = %.10e\n', p);

[h,p] = kstest2(all_speeds.emp.mid, all_speeds.pr.mid);
fprintf('Emp vs Phase (mid): p = %.10e\n', p);

[h,p] = kstest2(all_speeds.emp.mid, all_speeds.sh.mid);
fprintf('Emp vs Shuffled (mid): p = %.10e\n', p);

fprintf('\n===== MEAN SPEEDS =====\n')

fprintf('Emp long: %.4f\n', mean(all_speeds.emp.long));
fprintf('Phase long: %.4f\n', mean(all_speeds.pr.long));
fprintf('Shuffled long: %.4f\n\n', mean(all_speeds.sh.long));

fprintf('Emp mid: %.4f\n', mean(all_speeds.emp.mid));
fprintf('Phase mid: %.4f\n', mean(all_speeds.pr.mid));
fprintf('Shuffled mid: %.4f\n', mean(all_speeds.sh.mid));

%% ========================================================================
%  REPRODUCTION FINALE DE LA FIGURE 4D (N=49 SUJETS, TR=2.0)
%% ========================================================================

% 1. PARAMÈTRES
N = 49; 
TR = 2.0; 
win_ranges = { [60 210], [15 60] }; % Secondes
range_names = {'Long Windows (60-210s)', 'Mid Windows (15-60s)'};

% Stockage : [Sujets x Conditions (Emp, PR, SH)]
Vtyp_results = cell(2,1); 
for r = 1:2, Vtyp_results{r} = zeros(N, 3); end

fprintf('Calcul des Vtyp pour le groupe (%d sujets)...\n', N);

% 2. BOUCLE DE TRAITEMENT
for s = 1:N
    SUBJECT = eval(sprintf('SUBJECT_%d', s));
    TS_emp = SUBJECT.TS;
    
    % --- Génération des Surrogates ---
    % Phase-randomized (Null hypothesis: stationarity) [cite: 521, 527]
    TS_pr = PhaseRand_surrogates(TS_emp); 
    
    for r = 1:2
        w_range = round(win_ranges{r} / TR);
        tmp_e = []; tmp_p = []; tmp_s = [];
        
        % On parcourt la gamme de fenêtres [cite: 523]
        for w = w_range(1):10:w_range(2)
            % Flux dFC
            s_emp = TS2dFCstream(TS_emp, w, 1);
            s_pr  = TS2dFCstream(TS_pr, w, 1);
            % Shuffled (Null hypothesis: no seq. correlations) [cite: 522, 535]
            s_sh  = s_emp(:, randperm(size(s_emp, 2))); 
            
            % Vitesses instantanées [cite: 274]
            [~, v_e] = dFC_Speeds(s_emp, w);
            [~, v_p] = dFC_Speeds(s_pr, w);
            [~, v_s] = dFC_Speeds(s_sh, w);
            
            tmp_e = [tmp_e; v_e]; tmp_p = [tmp_p; v_p]; tmp_s = [tmp_s; v_s];
        end
        
        % Extraction du Vtyp (Vitesse typique par sujet) [cite: 20, 73]
        Vtyp_results{r}(s, 1) = median(tmp_e);
        Vtyp_results{r}(s, 2) = median(tmp_p);
        Vtyp_results{r}(s, 3) = median(tmp_s);
    end
    if mod(s,10)==0, fprintf('Sujet %d/49 terminé\n', s); end
end

%% ========================================================================
% 3. VISUALISATION ET TESTS STATISTIQUES (KS-TEST)
%% ========================================================================
figure('Name', 'Figure 4D - dFC Speed Distributions', 'Color', 'k');

for r = 1:2
    subplot(2, 1, r); hold on;
    data = Vtyp_results{r};
    
    % KDE [cite: 523]
    [f1, x1] = ksdensity(data(:,1)); % Empirique (Bleu)
    [f2, x2] = ksdensity(data(:,2)); % Phase Rand (Vert)
    [f3, x3] = ksdensity(data(:,3)); % Shuffled (Rouge)
    
    % Tracé des courbes [cite: 523]
    p1 = plot(x1, f1, 'Color', [0.1 0.1 0.5], 'LineWidth', 3, 'DisplayName', 'Empirical');
    p2 = plot(x2, f2, 'g--', 'LineWidth', 2, 'DisplayName', 'Phase rand');
    p3 = plot(x3, f3, 'r:', 'LineWidth', 2, 'DisplayName', 'Shuffled');
    
    % Tests de Kolmogorov-Smirnov 
    [~, p_pr] = kstest2(data(:,1), data(:,2));
    [~, p_sh] = kstest2(data(:,1), data(:,3));
    
    % Ajout des étoiles de significativité 
    y_max = max([f1, f2, f3]);
    if p_pr < 0.01, text(x1(f1==max(f1))-0.05, max(f1)+0.1, '**', 'Color', 'g', 'FontSize', 15); end
    if p_sh < 0.01, text(x1(f1==max(f1))+0.05, max(f1)+0.1, '**', 'Color', 'r', 'FontSize', 15); end

    title(range_names{r}); xlabel('V_{typ}'); ylabel('Prob. density');
    legend([p1 p2 p3], 'Location', 'northeast', 'Box', 'off');
    grid on; xlim([0 1.2]);
end

%% ========================================================================
%  ANALYSE DES TRIMERS (HIGH-ORDER ORGANIZATION) - MÉTHODE ARBABYAZD
%% ========================================================================

N_nodes = 68;
N_subjects = 49;
trimer_strength_all = zeros(N_subjects, 1);

% 1. Création de la table de correspondance (Mapping Arêtes -> Index MC)
% On suit l'ordre du triu(true(N_nodes), 1) utilisé dans dFCstream
[row_idx, col_idx] = find(triu(true(N_nodes), 1));
n_edges = length(row_idx); % Doit être 2278

% Matrice pour retrouver l'index de l'arête (i,j) rapidement
edge_map = zeros(N_nodes, N_nodes);
for e = 1:n_edges
    edge_map(row_idx(e), col_idx(e)) = e;
    edge_map(col_idx(e), row_idx(e)) = e;
end

fprintf('Calcul des Trimers pour %d sujets...\n', N_subjects);

for s = 1:N_subjects
    SUBJECT = eval(sprintf('SUBJECT_%d', s));
    
    % Calcul de la MC individuelle
    MC_sub = dFCstream2MC(SUBJECT.dFCstream);
    
    % On ne s'intéresse qu'aux triplets de régions (i, j, k)
    % Nombre de triplets possibles : 68*67*66 / 6 = 50 116
    t_strengths = [];
    
    % On boucle sur tous les triangles possibles
    for i = 1:N_nodes
        for j = i+1:N_nodes
            for k = j+1:N_nodes
                
                % Récupérer les indices des 3 arêtes formant le triangle
                e1 = edge_map(i, j);
                e2 = edge_map(j, k);
                e3 = edge_map(i, k);
                
                % Trimer Strength = Moyenne des corrélations entre ces arêtes
                % Formule tirée d'Arbabyazd et al. (2023)
                t_val = (MC_sub(e1, e2) + MC_sub(e2, e3) + MC_sub(e1, e3)) / 3;
                t_strengths(end+1) = t_val;
            end
        end
    end
    
    % Force moyenne des trimers pour le sujet
    trimer_strength_all(s) = mean(t_strengths);
    
    if mod(s,10) == 0, fprintf('Sujet %d/49 terminé\n', s); end
end

%% ========================================================================
%  STATISTIQUES ET VISUALISATION PAR GROUPE
%% ========================================================================

mean_trimer = zeros(3,1);
sem_trimer = zeros(3,1);

for k = 1:3
    idx = (groups == k); % Utilise tes groupes G1, G2, G3
    mean_trimer(k) = mean(trimer_strength_all(idx));
    sem_trimer(k)  = std(trimer_strength_all(idx)) / sqrt(sum(idx));
end

figure('Name', 'Trimer Strength vs Age', 'Color', 'k');
errorbar(1:3, mean_trimer, sem_trimer, '-s', 'LineWidth', 2, ...
    'MarkerSize', 10, 'MarkerFaceColor', 'b', 'CapSize', 10);

set(gca, 'XTick', 1:3, 'XTickLabel', {'Young (G1)', 'Middle (G2)', 'Old (G3)'});
ylabel('Global Trimer Strength (tMC)');
title('Évolution de l''organisation d''ordre supérieur avec l''âge');
grid on;

% Test de corrélation global
[r_trim, p_trim] = corr(ages, trimer_strength_all);
fprintf('\nRésultat : r = %.3f, p = %.4f\n', r_trim, p_trim);

%% ========================================================================
%  FIGURE 6 RIGHT PANEL (PAR ROI)
%  Dimers / Trimers par région
%% ========================================================================

fprintf('\n===== REGIONAL DIMERS / TRIMERS =====\n')

% --- INIT ---
SUBJECT = SUBJECT_1;
dFCstream = SUBJECT.dFCstream;

nEdges = size(dFCstream,1);
nROI = round((1 + sqrt(1 + 8*nEdges))/2);

[ind_i, ind_j] = find(triu(ones(nROI),1));
edges = [ind_i ind_j];

% stockage
dimer_roi   = zeros(N, nROI);
trimer_roi  = zeros(N, nROI);

%% =========================
% LOOP SUJETS
%% =========================

for s = 1:N
    
    SUBJECT = eval(sprintf('SUBJECT_%d',s));
    dFCstream = SUBJECT.dFCstream;
    
    % --- DIMERS PAR ROI ---
    dimer_tmp = zeros(nROI,1);
    count_d = zeros(nROI,1);
    
    for e = 1:nEdges
        
        i = edges(e,1);
        j = edges(e,2);
        
        val = mean(abs(dFCstream(e,:)));
        
        dimer_tmp(i) = dimer_tmp(i) + val;
        dimer_tmp(j) = dimer_tmp(j) + val;
        
        count_d(i) = count_d(i) + 1;
        count_d(j) = count_d(j) + 1;
        
    end
    
    dimer_roi(s,:) = (dimer_tmp ./ count_d)';
    
    % --- MC ---
    MC = dFCstream2MC(dFCstream);
    
    % --- TRIMERS PAR ROI ---
    trimer_tmp = zeros(nROI,1);
    count_t = zeros(nROI,1);
    
    for e1 = 1:nEdges
        
        i = edges(e1,1);
        j = edges(e1,2);
        
        for e2 = e1+1:nEdges
            
            k = edges(e2,1);
            l = edges(e2,2);
            
            % partage un noeud → TRIMER
            shared_nodes = intersect([i j],[k l]);
            
            if ~isempty(shared_nodes)
                
                val = abs(MC(e1,e2));
                
                % contribution au noeud racine
                for node = shared_nodes
                    
                    trimer_tmp(node) = trimer_tmp(node) + val;
                    count_t(node) = count_t(node) + 1;
                    
                end
                
            end
            
        end
    end
    
    trimer_roi(s,:) = (trimer_tmp ./ count_t)';
    
    if mod(s,10)==0
        fprintf('Subject %d/%d done\n', s, N);
    end
    
end

%% =========================
% MOYENNE PAR GROUPE
%% =========================

dimer_group  = zeros(3,nROI);
trimer_group = zeros(3,nROI);

for g = 1:3
    
    idx = group == g;
    
    dimer_group(g,:)  = mean(dimer_roi(idx,:),1);
    trimer_group(g,:) = mean(trimer_roi(idx,:),1);
    
end

%% =========================
% PLOT (STYLE FIGURE 6)
%% =========================

figure

% ----- DIMERS -----
subplot(1,2,1)
hold on

plot(dimer_group(1,:), 'LineWidth',2)
plot(dimer_group(2,:), 'LineWidth',2)
plot(dimer_group(3,:), 'LineWidth',2)

xlabel('ROI')
ylabel('Dimer strength')

title('Dimers (par région)')

legend('Young','Middle','Old')
grid on

% ----- TRIMERS -----
subplot(1,2,2)
hold on

plot(trimer_group(1,:), 'LineWidth',2)
plot(trimer_group(2,:), 'LineWidth',2)
plot(trimer_group(3,:), 'LineWidth',2)

xlabel('ROI')
ylabel('Trimer strength')

title('Trimers (par région)')

legend('Young','Middle','Old')
grid on

colormap(turbo)

%% 2. STATISTIQUES ET PRÉPARATION DES GRAPHIQUES
% Moyenne globale pour identifier les Hubs
mean_nodal_tMC = mean(nodal_tMC_all, 1);

% --- NOUVEAU : CALCUL DU SEUIL (Threshold) ---
% On définit le seuil au 80ème percentile (Top 20% des régions)
threshold_hubs = prctile(mean_nodal_tMC, 80); 
% ---------------------------------------------

[sorted_hubs, idx_hubs] = sort(mean_nodal_tMC, 'ascend');

% Corrélations avec l'âge (inchangé)
r_age = zeros(N_nodes, 1);
p_age = zeros(N_nodes, 1);
for i = 1:N_nodes
    [r_age(i), p_age(i)] = corr(ages, nodal_tMC_all(:, i));
end
[sorted_r, idx_r] = sort(r_age, 'ascend');

%% 3. GÉNÉRATION DES FIGURES
figure('Name', 'Analyse Régionale des Trimères', 'Color', 'k', 'Units', 'normalized', 'Position', [0.1 0.1 0.8 0.8]);

% --- GRAPH A : Nodal Trimer Strength (Identification des Meta-hubs) ---
subplot(1, 2, 1);
b1 = barh(1:N_nodes, sorted_hubs, 'FaceColor', [0.3 0.3 0.3], 'EdgeColor', 'none');
hold on;

% Colorer uniquement les régions qui dépassent le seuil
for m = 1:N_nodes
    if sorted_hubs(m) >= threshold_hubs
        % On utilise une couleur Or/Ambre pour les hubs significatifs
        patch([0 sorted_hubs(m) sorted_hubs(m) 0], [m-0.4 m-0.4 m+0.4 m+0.4], [0.9 0.6 0.1], 'EdgeColor', 'none');
    end
end

% Ajouter une ligne verticale pour visualiser le seuil
xline(threshold_hubs, '--w', 'Label', 'Seuil (Top 20%)', 'LabelOrientation', 'aligned', 'Color', [0.5 0.5 0.5]);

set(gca, 'Color', 'k', 'XColor', 'w', 'YColor', 'w', 'FontSize', 7);
set(gca, 'YTick', 1:N_nodes, 'YTickLabel', labels_68(idx_hubs)); 
xlabel('Nodal Trimer Strength (tMC)');
title(['A. Meta-hubs (Seuil > ', num2str(threshold_hubs, '%.2f'), ')'], 'Color', 'w', 'FontSize', 12);
grid on; set(gca, 'GridColor', [0.2 0.2 0.2]);

% --- GRAPH B : Effet de l'Âge (Reste identique mais intégré pour la cohérence) ---
subplot(1, 2, 2);
b2 = barh(1:N_nodes, sorted_r, 'FaceColor', 'flat', 'EdgeColor', 'none');
for i = 1:N_nodes
    actual_roi_idx = idx_r(i);
    if p_age(actual_roi_idx) < 0.05
        b2.CData(i, :) = [0.8 0.2 0.2]; % Rouge si significatif
    else
        b2.CData(i, :) = [0.4 0.4 0.4]; % Gris sinon
    end
end

set(gca, 'Color', 'k', 'XColor', 'w', 'YColor', 'w', 'FontSize', 7);
set(gca, 'YTick', 1:N_nodes, 'YTickLabel', labels_68(idx_r));
xlabel('Corrélation avec l''Âge (Pearson r)');
title('B. Sensibilité au Vieillissement (Rouge: p < 0.05)', 'Color', 'w', 'FontSize', 12);
grid on; set(gca, 'GridColor', [0.2 0.2 0.2]);

sgtitle('Organisation Spatio-temporelle des Trimères (Analyse par Threshold)', 'Color', 'w', 'FontSize', 16);

%%% ========================================================================
%  META-HUBS + VALEURS BRUTES + BARRES D'ERREUR
%% ========================================================================

fprintf('\n===== META-HUBS (RAW VALUES + SEM) =====\n')

%% =========================
% ROI NAMES
%% =========================

ROI_names = cell(1, 68);
k = 1;

for i = 1:length(regions_base)
    ROI_names{k}   = [regions_base{i} '_L'];
    ROI_names{k+1} = [regions_base{i} '_R'];
    k = k + 2;
end

ROI_names = ROI_names(1:nROI);

%% =========================
% META-HUBS (BASED ON TRIMERS)
%% =========================

trimer_importance = mean(trimer_group,1);

threshold = prctile(trimer_importance, 80);
meta_hubs = find(trimer_importance >= threshold);

fprintf('Meta-hubs: %d / %d\n', length(meta_hubs), nROI)

%% =========================
% COMPUTE MEAN + SEM PAR GROUPE
%% =========================

dimer_mean  = zeros(3,nROI);
dimer_sem   = zeros(3,nROI);

trimer_mean = zeros(3,nROI);
trimer_sem  = zeros(3,nROI);

for g = 1:3
    
    idx = group == g;
    
    dimer_mean(g,:)  = mean(dimer_roi(idx,:),1);
    trimer_mean(g,:) = mean(trimer_roi(idx,:),1);
    
    dimer_sem(g,:)  = std(dimer_roi(idx,:),[],1) ./ sqrt(sum(idx));
    trimer_sem(g,:) = std(trimer_roi(idx,:),[],1) ./ sqrt(sum(idx));
    
end

%% =========================
% SUBPLOT ORGANISATION
%% =========================

nHubs = length(meta_hubs);
ncols = ceil(sqrt(nHubs));
nrows = ceil(nHubs / ncols);

colors = [ ...
    0 0.6 0.3;    % G1 (vert comme papier)
    0.8 0.8 0.2;  % G2 (jaune)
    0.85 0.33 0.10 % G3 (orange/rouge)
];

%% =========================
% FIGURE DIMERS
%% =========================

figure('Name','Dimers (Meta-hubs)','Color','k')

for idx = 1:nHubs
    
    r = meta_hubs(idx);
    
    subplot(nrows, ncols, idx)
    hold on
    
    vals = dimer_mean(:,r);
    err  = dimer_sem(:,r);
    
    for g = 1:3
        bar(g, vals(g), 'FaceColor', colors(g,:), 'EdgeColor','none')
    end
    
    errorbar(1:3, vals, err, 'w', 'LineStyle','none', 'LineWidth',1)
    
    xticks([1 2 3])
    xticklabels({'Jeune','Moyen','Agée'}) % adapte si besoin
    
    title(ROI_names{r}, 'Interpreter','none')
    
    ylim([0 0.6])
    grid on
    
end

sgtitle('Interzone Dimer Strength (Meta-hubs)')

%% =========================
% FIGURE TRIMERS
%% =========================

figure('Name','Trimers (Meta-hubs)','Color','k')

for idx = 1:nHubs
    
    r = meta_hubs(idx);
    
    subplot(nrows, ncols, idx)
    hold on
    
    vals = trimer_mean(:,r);
    err  = trimer_sem(:,r);
    
    for g = 1:3
        bar(g, vals(g), 'FaceColor', colors(g,:), 'EdgeColor','none')
    end
    
    errorbar(1:3, vals, err, 'w', 'LineStyle','none', 'LineWidth',1)
    
    xticks([1 2 3])
    xticklabels({'Jeune','Moyen','Agée'})
    
    title(ROI_names{r}, 'Interpreter','none')
    
    ylim([0 0.6]) 
    grid on
    
end

sgtitle('Interzone Trimer Strength (Meta-hubs)')

fprintf('\n===== DONE =====\n')

%% ========================================================================
%  GRAPH : MÉTA-CONNECTIVITÉ (MC) TRIÉE PAR MODULES (FIX SIZE ERROR)
%% ========================================================================

% 1. DÉTERMINER LA TAILLE RÉELLE (Évite l'erreur de taille incompatible)
SUB_temp = eval(sprintf('SUBJECT_%d', 1));
MC_example = dFCstream2MC(SUB_temp.dFCstream); 
[n_mc, ~] = size(MC_example); % Récupère la taille réelle (ex: 2278)

MC_mean_groups = zeros(n_mc, n_mc, 3);
titles_mc = {'Jeunes (G1)', 'Moyens (G2)', 'Seniors (G3)'};

% 2. CALCUL DES MOYENNES PAR GROUPE
fprintf('Extraction et moyenne des MC pour %d sujets...\n', N);
for k = 1:3
    idx_g = find(groups == k);
    sum_mc = zeros(n_mc, n_mc);
    
    for i = 1:length(idx_g)
        S = eval(sprintf('SUBJECT_%d', idx_g(i)));
        MC_sub = dFCstream2MC(S.dFCstream);
        
        % Vérification de sécurité pour la taille
        if size(MC_sub, 1) == n_mc
            sum_mc = sum_mc + MC_sub;
        else
            warning('Sujet %d ignoré : taille MC incompatible (%dx%d)', idx_g(i), size(MC_sub,1), size(MC_sub,2));
        end
    end
    MC_mean_groups(:,:,k) = sum_mc / length(idx_g);
end

%% ========================================================================
%  AFFICHAGE DE LA MC EXISTANTE (TRIÉE PAR MODULES, GESTION NÉGATIFS)
%% ========================================================================
% Ce code suppose que 'MC_mean_groups' ($N_{edges} \times N_{edges} \times 3$)
% est déjà dans votre workspace.

% 1. VÉRIFICATION ET INITIALISATION
if ~exist('MC_mean_groups', 'var')
    error('La variable MC_mean_groups n''est pas dans le workspace. Impossible d''afficher.');
end

n_mc = size(MC_mean_groups, 1); % Nombre de connexions (ex: 2278)
titles_mc = {'Jeunes (G1)', 'Moyens (G2)', 'Seniors (G3)'};

fprintf('Variable détectée (%dx%d). Préparation de l''affichage...\n', n_mc, n_mc);

% 2. DÉTECTION DES MODULES SUR G1 (Correction Poids Négatifs)
% On utilise G1 comme référence pour définir l'ordre des lignes/colonnes
fprintf('Détection des méta-modules sur G1 (Option negative_sym)...\n');
MC_ref = MC_mean_groups(:,:,1);
MC_ref(logical(eye(n_mc))) = 0; % Mise à zéro de la diagonale

% Paramètres Louvain adaptés (gamma=1.1, gestion symétrique des négatifs)
gamma_mc = 1.1; 
[Ci_mc, ~] = community_louvain(MC_ref, gamma_mc, [], 'negative_sym');

% Tri des indices pour regrouper les modules sur la diagonale
[Ci_sorted_mc, idx_sort_mc] = sort(Ci_mc);


% 3. GÉNÉRATION DE LA FIGURE COMPARATIVE
figure('Name', 'Méta-Connectivité : Comparaison par Groupes d''Âge', ...
       'Color', 'k', 'Units', 'normalized', 'Position', [0.05 0.2 0.9 0.5]);

for k = 1:3
    subplot(1, 3, k);
    
    % Application du tri de G1 à la matrice du groupe k
    MC_plot = MC_mean_groups(idx_sort_mc, idx_sort_mc, k);
    MC_plot(logical(eye(n_mc))) = 0; % Diagonale à zéro pour le plot
    
    % Affichage
    imagesc(MC_plot);
    axis square; 
    colormap(turbo); % Contraste élevé
    colorbar;
    clim([0 0.4]); % Limites ajustées pour voir la structure moyenne
    
    % Esthétique (Fond noir, texte blanc)
    set(gca, 'Color', 'k', 'XColor', 'w', 'YColor', 'w', 'FontSize', 9);
    title(titles_mc{k}, 'Color', 'w', 'FontSize', 14, 'FontWeight', 'bold');
    
    if k == 1
        ylabel('Connexions (triées par modules G1)', 'Color', 'w');
    end
    xlabel('Connexions (triées)', 'Color', 'w');
    
    % TRACÉ DES FRONTIÈRES DES MODULES
    hold on;
    pos = 0;
    u_mod = unique(Ci_sorted_mc);
    for m = 1:length(u_mod)
        n_in_mod = sum(Ci_sorted_mc == u_mod(m)); % Taille du module
        pos = pos + n_in_mod;
        % Lignes pointillées blanches discrètes
        line([pos pos], [0 n_mc], 'Color', [1 1 1 0.3], 'LineWidth', 0.5, 'LineStyle', ':');
        line([0 n_mc], [pos pos], 'Color', [1 1 1 0.3], 'LineWidth', 0.5, 'LineStyle', ':');
    end
end

% Titre principal
sgtitle('Organisation Modulaire de la Méta-Connectivité (Référence G1)', ...
        'Color', 'w', 'FontSize', 18, 'FontWeight', 'bold');

fprintf('Affichage terminé.\n');

%% =========================
% META-HUBS / ROI SELECTION (MODULE-WISE, FLEXIBLE)
%% =========================

% modules : vecteur [1 x nROI]
% group   : vecteur groupe sujet
% dimer_roi, trimer_roi : [nSubjects x nROI]

unique_modules = unique(modules);
selected_rois = [];

% ===== CHOIX DU MODE =====
selection_mode = 'all';  
% 'all'           -> toutes les ROI
% 'low_threshold' -> seuil faible par module
% 'topk'          -> top k par module

low_percentile = 30;   % seuil faible si mode = 'low_threshold'
k_fixed = 3;           % nb de ROI par module si mode = 'topk'

for m = unique_modules
    
    roi_in_module = find(modules == m);
    values = mean(trimer_roi(:, roi_in_module), 1, 'omitnan');
    
    switch selection_mode
        
        case 'all'
            rois_module = roi_in_module;
            
        case 'low_threshold'
            thr = prctile(values, low_percentile);
            rois_module = roi_in_module(values >= thr);
            
            % sécurité
            if isempty(rois_module)
                [~, idx_max] = max(values);
                rois_module = roi_in_module(idx_max);
            end
            
        case 'topk'
            k = min(k_fixed, length(roi_in_module));
            [~, idx_sorted] = sort(values, 'descend');
            rois_module = roi_in_module(idx_sorted(1:k));
            
        otherwise
            error('selection_mode inconnu');
    end
    
    selected_rois = [selected_rois rois_module];
    
    fprintf('Module %d : %d ROI sélectionnées\n', m, length(rois_module));
end

selected_rois = unique(selected_rois, 'stable');

fprintf('ROI sélectionnées total : %d / %d\n', length(selected_rois), nROI);
disp('Indices ROI sélectionnées :')
disp(selected_rois)
disp('Noms ROI sélectionnées :')
disp(ROI_names(selected_rois))


%% =========================
% COMPUTE MEAN + SEM PAR GROUPE
%% =========================

dimer_mean  = zeros(3,nROI);
dimer_sem   = zeros(3,nROI);

trimer_mean = zeros(3,nROI);
trimer_sem  = zeros(3,nROI);

for g = 1:3
    
    idx = (group == g);
    
    dimer_mean(g,:)  = mean(dimer_roi(idx,:), 1, 'omitnan');
    trimer_mean(g,:) = mean(trimer_roi(idx,:), 1, 'omitnan');
    
    dimer_sem(g,:)  = std(dimer_roi(idx,:), 0, 1, 'omitnan') ./ sqrt(sum(idx));
    trimer_sem(g,:) = std(trimer_roi(idx,:), 0, 1, 'omitnan') ./ sqrt(sum(idx));
    
end


%% =========================
% SUBPLOT ORGANISATION
%% =========================

nSel = length(selected_rois);
ncols = ceil(sqrt(nSel));
nrows = ceil(nSel / ncols);

% couleurs : dimers = tons pleins, trimers = tons plus clairs
colors_dimer = [ ...
    0.00 0.60 0.30;
    0.80 0.80 0.20;
    0.85 0.33 0.10
];

colors_trimer = [ ...
    0.40 0.85 0.65;
    0.95 0.95 0.55;
    1.00 0.55 0.35
];


%% =========================
% FIGURE UNIQUE : DIMER + TRIMER DANS LE MEME SUBPLOT
%% =========================

figure('Name','Dimers + Trimers (Module-wise)','Color','k')

for i = 1:nSel
    
    r = selected_rois(i);
    subplot(nrows, ncols, i)
    hold on
    
    % positions barres
    x_dimer  = [1 2 3];
    x_trimer = [1.35 2.35 3.35];
    
    vals_d = dimer_mean(:,r);
    err_d  = dimer_sem(:,r);
    
    vals_t = trimer_mean(:,r);
    err_t  = trimer_sem(:,r);
    
    % DIMER
    for g = 1:3
        bar(x_dimer(g), vals_d(g), 0.28, ...
            'FaceColor', colors_dimer(g,:), ...
            'EdgeColor', 'none');
    end
    
    % TRIMER
    for g = 1:3
        bar(x_trimer(g), vals_t(g), 0.28, ...
            'FaceColor', colors_trimer(g,:), ...
            'EdgeColor', 'none');
    end
    
    % erreurs
    errorbar(x_dimer, vals_d, err_d, 'w', 'LineStyle', 'none', 'LineWidth', 1)
    errorbar(x_trimer, vals_t, err_t, 'w', 'LineStyle', 'none', 'LineWidth', 1)
    
    xticks([1.175 2.175 3.175])
    xticklabels({'Jeune','Moyen','Agée'})
    
    title(sprintf('%s (M%d)', ROI_names{r}, modules(r)), 'Interpreter', 'none')
    
    ylabel('Strength')
    grid on
    box off
    
    % adapte automatiquement la limite Y
    ymax = max([vals_d + err_d; vals_t + err_t], [], 'all');
    if isempty(ymax) || isnan(ymax) || ymax <= 0
        ymax = 0.1;
    end
    ylim([0 ymax * 1.25])
    
    % légende seulement sur le premier subplot
    if i == 1
        h1 = bar(nan, nan, 'FaceColor', colors_dimer(1,:), 'EdgeColor', 'none');
        h2 = bar(nan, nan, 'FaceColor', colors_trimer(1,:), 'EdgeColor', 'none');
        legend([h1 h2], {'Dimer','Trimer'}, 'Location', 'best')
    end
end

sgtitle(sprintf('Dimer + Trimer Strength par ROI (%s)', selection_mode))

fprintf('\n===== DONE =====\n')

%% =========================
% INTRA vs INTER MODULAR ANALYSIS
% (ROI-level approximation)
%% =========================

% Variables attendues :
% dimer_roi   : [49 x 68]
% trimer_roi  : [49 x 68]
% Ci          : [68 x 1]  -> module de chaque ROI
% group       : [49 x 1] ou [1 x 49]

%% =========================
% BASIC SIZES
%% =========================

nSub = size(dimer_roi,1);
nROI = size(dimer_roi,2);

if size(trimer_roi,1) ~= nSub || size(trimer_roi,2) ~= nROI
    error('dimer_roi et trimer_roi n''ont pas la même taille.');
end

group = group(:);
modules = Ci(:)';   % <- FIX IMPORTANT

if length(modules) ~= nROI
    error('Le vecteur Ci ne correspond pas au nombre de ROI.');
end

fprintf('Taille dimer_roi  : [%d x %d]\n', size(dimer_roi,1), size(dimer_roi,2));
fprintf('Taille trimer_roi : [%d x %d]\n', size(trimer_roi,1), size(trimer_roi,2));
fprintf('Taille modules    : [%d x %d]\n', size(modules,1), size(modules,2));

%% =========================
% COMPUTE INTRA / INTER PAR ROI
%% =========================

intra_dimer  = NaN(nSub, nROI);
inter_dimer  = NaN(nSub, nROI);

intra_trimer = NaN(nSub, nROI);
inter_trimer = NaN(nSub, nROI);

for r = 1:nROI
    
    same_module  = (modules == modules(r));
    other_module = (modules ~= modules(r));
    
    % enlever la ROI elle-même du intra
    same_module(r) = false;
    
    % intra
    if any(same_module)
        intra_dimer(:,r)  = mean(dimer_roi(:, same_module), 2, 'omitnan');
        intra_trimer(:,r) = mean(trimer_roi(:, same_module), 2, 'omitnan');
    end
    
    % inter
    if any(other_module)
        inter_dimer(:,r)  = mean(dimer_roi(:, other_module), 2, 'omitnan');
        inter_trimer(:,r) = mean(trimer_roi(:, other_module), 2, 'omitnan');
    end
end

fprintf('Intra/inter ROI-level calculés.\n');

%% =========================
% MOYENNE GLOBALE PAR SUJET
%% =========================

subj_intra_dimer  = mean(intra_dimer,  2, 'omitnan');
subj_inter_dimer  = mean(inter_dimer,  2, 'omitnan');

subj_intra_trimer = mean(intra_trimer, 2, 'omitnan');
subj_inter_trimer = mean(inter_trimer, 2, 'omitnan');

%% =========================
% STATS PAR GROUPE
%% =========================

nGroups = 3;

intra_d_mean  = NaN(nGroups,1);
inter_d_mean  = NaN(nGroups,1);
intra_t_mean  = NaN(nGroups,1);
inter_t_mean  = NaN(nGroups,1);

intra_d_sem   = NaN(nGroups,1);
inter_d_sem   = NaN(nGroups,1);
intra_t_sem   = NaN(nGroups,1);
inter_t_sem   = NaN(nGroups,1);

for g = 1:nGroups
    
    idx = (group == g);
    
    intra_d_mean(g) = mean(subj_intra_dimer(idx), 'omitnan');
    inter_d_mean(g) = mean(subj_inter_dimer(idx), 'omitnan');
    
    intra_t_mean(g) = mean(subj_intra_trimer(idx), 'omitnan');
    inter_t_mean(g) = mean(subj_inter_trimer(idx), 'omitnan');
    
    intra_d_sem(g) = std(subj_intra_dimer(idx), 'omitnan') / sqrt(sum(idx));
    inter_d_sem(g) = std(subj_inter_dimer(idx), 'omitnan') / sqrt(sum(idx));
    
    intra_t_sem(g) = std(subj_intra_trimer(idx), 'omitnan') / sqrt(sum(idx));
    inter_t_sem(g) = std(subj_inter_trimer(idx), 'omitnan') / sqrt(sum(idx));
end

%% =========================
% AFFICHAGE NUMERIQUE
%% =========================

fprintf('\n===== GROUP RESULTS =====\n');
for g = 1:nGroups
    fprintf('Groupe %d\n', g);
    fprintf('  Dimer  intra = %.4f ± %.4f\n', intra_d_mean(g), intra_d_sem(g));
    fprintf('  Dimer  inter = %.4f ± %.4f\n', inter_d_mean(g), inter_d_sem(g));
    fprintf('  Trimer intra = %.4f ± %.4f\n', intra_t_mean(g), intra_t_sem(g));
    fprintf('  Trimer inter = %.4f ± %.4f\n\n', inter_t_mean(g), inter_t_sem(g));
end

%% =========================
% FIGURE 1 : COURBES GLOBALES
%% =========================

figure('Name','Intra vs Inter - Global','Color','w');
hold on

x = 1:nGroups;

errorbar(x, intra_d_mean, intra_d_sem, '-o', 'LineWidth', 2, 'MarkerSize', 7)
errorbar(x, inter_d_mean, inter_d_sem, '--o', 'LineWidth', 2, 'MarkerSize', 7)

errorbar(x, intra_t_mean, intra_t_sem, '-s', 'LineWidth', 2, 'MarkerSize', 7)
errorbar(x, inter_t_mean, inter_t_sem, '--s', 'LineWidth', 2, 'MarkerSize', 7)

xticks([1 2 3])
xticklabels({'Jeune','Moyen','Agée'})

ylabel('Strength')
title('Intra vs Inter Modular Strength')
legend({'Dimer Intra','Dimer Inter','Trimer Intra','Trimer Inter'}, 'Location','best')
grid on
box off

%% =========================
% FIGURE 2 : BARPLOT
%% =========================

figure('Name','Intra vs Inter - Bars','Color','w')

colors = [
    0.00 0.60 0.30
    0.80 0.80 0.20
    0.85 0.33 0.10
];

subplot(1,2,1)
hold on

x_intra = [1 2 3];
x_inter = [1.35 2.35 3.35];

for g = 1:nGroups
    bar(x_intra(g), intra_d_mean(g), 0.28, 'FaceColor', colors(g,:), 'EdgeColor', 'none');
    bar(x_inter(g), inter_d_mean(g), 0.28, 'FaceColor', colors(g,:)*0.6 + 0.4, 'EdgeColor', 'none');
end

errorbar(x_intra, intra_d_mean, intra_d_sem, 'k', 'LineStyle','none', 'LineWidth',1)
errorbar(x_inter, inter_d_mean, inter_d_sem, 'k', 'LineStyle','none', 'LineWidth',1)

xticks([1.175 2.175 3.175])
xticklabels({'Jeune','Moyen','Agée'})
ylabel('Dimer strength')
title('Dimer : Intra vs Inter')
legend({'Intra','Inter'}, 'Location','best')
grid on
box off

subplot(1,2,2)
hold on

for g = 1:nGroups
    bar(x_intra(g), intra_t_mean(g), 0.28, 'FaceColor', colors(g,:), 'EdgeColor', 'none');
    bar(x_inter(g), inter_t_mean(g), 0.28, 'FaceColor', colors(g,:)*0.6 + 0.4, 'EdgeColor', 'none');
end

errorbar(x_intra, intra_t_mean, intra_t_sem, 'k', 'LineStyle','none', 'LineWidth',1)
errorbar(x_inter, inter_t_mean, inter_t_sem, 'k', 'LineStyle','none', 'LineWidth',1)

xticks([1.175 2.175 3.175])
xticklabels({'Jeune','Moyen','Agée'})
ylabel('Trimer strength')
title('Trimer : Intra vs Inter')
legend({'Intra','Inter'}, 'Location','best')
grid on
box off

sgtitle('Intra vs Inter Modular Analysis')

%% =========================
% FIGURE 3 : PAR MODULE (AVEC BARRES D'ERREUR)
%% =========================

unique_modules = unique(modules);
nMod = length(unique_modules);

module_intra_d = NaN(nGroups, nMod);
module_inter_d = NaN(nGroups, nMod);
module_intra_t = NaN(nGroups, nMod);
module_inter_t = NaN(nGroups, nMod);

% 👉 SEM
module_intra_d_sem = NaN(nGroups, nMod);
module_inter_d_sem = NaN(nGroups, nMod);
module_intra_t_sem = NaN(nGroups, nMod);
module_inter_t_sem = NaN(nGroups, nMod);

for im = 1:nMod
    
    m = unique_modules(im);
    roi_idx = (modules == m);
    
    subj_mod_intra_d = mean(intra_dimer(:, roi_idx), 2, 'omitnan');
    subj_mod_inter_d = mean(inter_dimer(:, roi_idx), 2, 'omitnan');
    
    subj_mod_intra_t = mean(intra_trimer(:, roi_idx), 2, 'omitnan');
    subj_mod_inter_t = mean(inter_trimer(:, roi_idx), 2, 'omitnan');
    
    for g = 1:nGroups
        idx = (group == g);
        
        % ===== MEAN =====
        module_intra_d(g,im) = mean(subj_mod_intra_d(idx), 'omitnan');
        module_inter_d(g,im) = mean(subj_mod_inter_d(idx), 'omitnan');
        
        module_intra_t(g,im) = mean(subj_mod_intra_t(idx), 'omitnan');
        module_inter_t(g,im) = mean(subj_mod_inter_t(idx), 'omitnan');
        
        % ===== SEM =====
        module_intra_d_sem(g,im) = std(subj_mod_intra_d(idx), 'omitnan') / sqrt(sum(idx));
        module_inter_d_sem(g,im) = std(subj_mod_inter_d(idx), 'omitnan') / sqrt(sum(idx));
        
        module_intra_t_sem(g,im) = std(subj_mod_intra_t(idx), 'omitnan') / sqrt(sum(idx));
        module_inter_t_sem(g,im) = std(subj_mod_inter_t(idx), 'omitnan') / sqrt(sum(idx));
    end
end

figure('Name','Intra vs Inter by Module','Color','k')

ncols = ceil(sqrt(nMod));
nrows = ceil(nMod / ncols);

for im = 1:nMod
    
    subplot(nrows, ncols, im)
    hold on
    
    x = 1:nGroups;
    
    % ===== COURBES =====
    plot(x, module_intra_d(:,im), '-o', 'LineWidth', 1.8)
    plot(x, module_inter_d(:,im), '--o', 'LineWidth', 1.8)
    plot(x, module_intra_t(:,im), '-s', 'LineWidth', 1.8)
    plot(x, module_inter_t(:,im), '--s', 'LineWidth', 1.8)
    
    % ===== BARRES D'ERREUR BLANCHES =====
    errorbar(x, module_intra_d(:,im), module_intra_d_sem(:,im), 'w', 'LineStyle','none', 'LineWidth',1)
    errorbar(x, module_inter_d(:,im), module_inter_d_sem(:,im), 'w', 'LineStyle','none', 'LineWidth',1)
    
    errorbar(x, module_intra_t(:,im), module_intra_t_sem(:,im), 'w', 'LineStyle','none', 'LineWidth',1)
    errorbar(x, module_inter_t(:,im), module_inter_t_sem(:,im), 'w', 'LineStyle','none', 'LineWidth',1)
    
    xticks([1 2 3])
    xticklabels({'Jeune','Moyen','Agée'})
    
    title(sprintf('Module %d', unique_modules(im)))
    
    grid on
    box off
end

sgtitle('Intra vs Inter per Module (avec SEM)')

fprintf('\n===== DONE =====\n');