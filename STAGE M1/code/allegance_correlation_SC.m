%% ================================
% PARAMÈTRES
% ================================
gamma   = 1;
n_runs  = 100;      % augmente pour probas plus stables

SUBJECT = SUBJECT_1;   % choisir un sujet
SC = SUBJECT.SC;

N_nodes = size(SC,1);
fprintf('Nombre de régions : %d\n', N_nodes);

% enlever diagonale
SC(1:N_nodes+1:end) = 0;
fprintf('Diagonale supprimée.\n');

%% ================================
% LOUVAIN MULTI-RUNS
% ================================
fprintf('Lancement Louvain (%d runs)...\n', n_runs);
Ci_runs = zeros(n_runs, N_nodes);

for r = 1:n_runs
    [Ci, Q] = community_louvain(SC, gamma);
    Ci_runs(r,:) = Ci;

    if mod(r,10)==0
        fprintf('  Run %d / %d terminé (Q = %.3f)\n', r, n_runs, Q);
    end
end
fprintf('Louvain terminé.\n');

%% ================================
% MATRICE DE CO-CLASSIFICATION
% ================================
fprintf('Calcul matrice de co-classification...\n');
D = agreement(Ci_runs');     % taille = N_nodes x N_nodes
P = D / n_runs;              % probabilité
fprintf('Matrice de probabilité calculée.\n');

%% ================================
% AFFICHAGE PROBAS
% ================================
figure;
imagesc(P);
colorbar;
title('Probabilité (SC) que deux régions soient dans le même module');
xlabel('Régions');
ylabel('Régions');
axis square;

%% ================================
% EXTRAIRE LES PAIRES LES PLUS STABLES
% ================================
fprintf('Extraction des paires les plus stables...\n');

P_no_diag = P;
P_no_diag(1:N_nodes+1:end) = 0;

[sorted_vals, idx] = sort(P_no_diag(:), 'descend');

topN = 20; % nombre de paires à afficher
fprintf('Top %d paires SC les plus souvent groupées :\n', topN);

for k = 1:topN
    [i,j] = ind2sub([N_nodes N_nodes], idx(k));
    fprintf('Région %d - Région %d : %.2f\n', i, j, sorted_vals(k));
end

%% ================================
% DONNÉES
% ================================
SC = SUBJECT_1.SC;
N  = size(SC,1);

% enlever diagonale
SC(1:N+1:end) = 0;

% partition (ex : consensus)
Ci = Ci_SC(1,:)';   % modules du sujet 1
fprintf('Partition SC chargée.\n');

%% ================================
% TRI PAR MODULE
% ================================
fprintf('Tri de la matrice SC par modules...\n');
[Ci_sorted, idx] = sort(Ci);
SC_sorted = SC(idx, idx);

%% ================================
% AFFICHAGE
% ================================
figure;
imagesc(SC_sorted);
colormap(jet);
colorbar;
axis square;
title('Matrice SC réordonnée par modules');

xlabel('Régions (triées par module)');
ylabel('Régions (triées par module)');

%% ================================
% LIGNES DE SÉPARATION ENTRE MODULES
% ================================
hold on;
modules = unique(Ci_sorted);
pos = 0;

for m = 1:length(modules)
    n_m = sum(Ci_sorted == modules(m));
    pos = pos + n_m;
    line([pos pos],[0 N],'Color','k','LineWidth',1.5)
    line([0 N],[pos pos],'Color','k','LineWidth',1.5)
end

fprintf('Affichage terminé.\n');