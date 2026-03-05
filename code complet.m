%CODE COMPLET STAGE

%% ============
% CODE 1
%% ============

load C:\Users\aure6\Downloads\STAGE_M1\code\Workspace
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
%  AFFICHAGE DU GRAPHIQUE COMPARAISON
%% ========================================================================
figure('Name', 'Analyses Topologiques : Efficiency vs Clustering', 'Color', 'k');

% --- SUBPLOT 1 : Global Efficiency (Intégration) ---
subplot(1,2,1);
errorbar(age_q, mean_E, sem_E, '-o', 'LineWidth', 2.5, 'MarkerSize', 8, ...
    'MarkerFaceColor', [0.8 0.2 0.2], 'Color', [0.8 0.2 0.2], 'CapSize', 10);
grid on;
title('Efficience Globale (Intégration)');
xlabel('Âge moyen du groupe');
ylabel('Global Efficiency');
set(gca, 'FontSize', 11);

% --- SUBPLOT 2 : Clustering Coefficient (Ségrégation locale) ---
subplot(1,2,2);
errorbar(age_q, mean_C, sem_C, '-o', 'LineWidth', 2.5, 'MarkerSize', 8, ...
    'MarkerFaceColor', [0.2 0.6 0.2], 'Color', [0.2 0.6 0.2], 'CapSize', 10);
grid on;
title('Coefficient de Clustering (Ségrégation locale)');
xlabel('Âge moyen du groupe');
ylabel('Mean Clustering Coefficient');
set(gca, 'FontSize', 11);

sgtitle('Évolution des propriétés du réseau avec l''âge (3 groupes)', 'FontSize', 14);

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
errorbar(age_mean_groups, mean_Qnorm_groups, sem_Qnorm_groups, '-o', ...
    'LineWidth', 2, 'MarkerSize', 10, 'MarkerFaceColor', [0.4 0.2 0.6], 'Color', [0.4 0.2 0.6]);

grid on;
xlabel('Âge moyen du groupe');
ylabel('(Q_{obs} - Q_{null}) / Q_{null}');
title('Évolution de la Modularité Normalisée (Excès de modularité)');
