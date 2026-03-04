%% ================================
% PARAMÈTRES
% ================================
gamma   = 1;
n_runs  = 100;      % augmente pour probas plus stables
N_nodes = size(SUBJECT_1.FC,1);

SUBJECT = SUBJECT_1;   % choisir un sujet
FC = SUBJECT.FC;
FC(1:N_nodes+1:end) = 0;

%% ================================
% LOUVAIN MULTI-RUNS
% ================================
Ci_runs = zeros(n_runs, N_nodes);

for r = 1:n_runs
    [Ci, ~] = community_louvain(FC, gamma, [], 'negative_sym');
    Ci_runs(r,:) = Ci;
end

%% ================================
% MATRICE DE CO-CLASSIFICATION
% ================================
D = agreement(Ci_runs');     % taille = N_nodes x N_nodes
P = D / n_runs;              % probabilité

%% ================================
% AFFICHAGE
% ================================
figure;
imagesc(P);
colorbar;
title('Probabilité que deux régions soient dans le même module');
xlabel('Régions');
ylabel('Régions');
axis square;

%% ================================
% EXTRAIRE LES PAIRES LES PLUS STABLES
% ================================
P_no_diag = P;
P_no_diag(1:N_nodes+1:end) = 0;

[sorted_vals, idx] = sort(P_no_diag(:), 'descend');

topN = 20; % nombre de paires à afficher
fprintf('Top %d paires les plus souvent groupées :\n', topN);

for k = 1:topN
    [i,j] = ind2sub([N_nodes N_nodes], idx(k));
    fprintf('Région %d - Région %d : %.2f\n', i, j, sorted_vals(k));
end

%% ================================
% DONNÉES
% ================================
FC = SUBJECT_1.FC;
N  = size(FC,1);

% enlever diagonale
FC(1:N+1:end) = 0;

% partition (ex : consensus)
Ci = Ci_FC(1,:)';   % modules du sujet 1

%% ================================
% TRI ET AFFICHAGE PAR MODULE
% ================================
[Ci_sorted, idx] = sort(Ci);
FC_sorted = FC(idx, idx);

figure;
imagesc(FC_sorted);
colormap(jet);
colorbar;
axis square;
title('Matrice FC réordonnée par modules');
xlabel('Régions (triées par module)');
ylabel('Régions (triées par module)');

% Lignes de séparation entre modules
hold on;
modules = unique(Ci_sorted);
pos = 0;
for m = 1:length(modules)
    n_m = sum(Ci_sorted == modules(m));
    pos = pos + n_m;
    line([pos pos],[0 N],'Color','k','LineWidth',1.5)
    line([0 N],[pos pos],'Color','k','LineWidth',1.5)
end