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