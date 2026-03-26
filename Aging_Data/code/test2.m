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

% 3. DÉTECTION DES MÉTA-MODULES (RÉFÉRENCE SUR G1)
fprintf('Détection des méta-modules sur G1...\n');
MC_ref = MC_mean_groups(:,:,1);
MC_ref(logical(eye(n_mc))) = 0; 

% Paramètres Louvain
gamma_mc = 1.1; 
[Ci_mc, ~] = community_louvain(MC_ref, gamma_mc);
[Ci_sorted_mc, idx_sort_mc] = sort(Ci_mc);

% 4. AFFICHAGE DES GRAPHES
figure('Name', 'Méta-Connectivité : Tri Modulaire par Groupe', 'Color', 'k', 'Units', 'normalized', 'Position', [0.05 0.3 0.9 0.4]);

for k = 1:3
    subplot(1, 3, k);
    
    % Tri de la matrice selon la référence G1
    MC_plot = MC_mean_groups(idx_sort_mc, idx_sort_mc, k);
    MC_plot(logical(eye(n_mc))) = 0;
    
    imagesc(MC_plot);
    axis square;
    colormap(turbo);
    colorbar;
    clim([0 0.4]); % Ajusté pour la visibilité des corrélations moyennes
    
    set(gca, 'Color', 'k', 'XColor', 'w', 'YColor', 'w', 'FontSize', 8);
    title(titles_mc{k}, 'Color', 'w', 'FontSize', 12);
    
    % Dessin des frontières de modules
    hold on;
    pos = 0;
    u_mod = unique(Ci_sorted_mc);
    for m = 1:length(u_mod)
        n_m = sum(Ci_sorted_mc == u_mod(m));
        pos = pos + n_m;
        line([pos pos], [0 n_mc], 'Color', [1 1 1 0.3], 'LineWidth', 0.5, 'LineStyle', ':');
        line([0 n_mc], [pos pos], 'Color', [1 1 1 0.3], 'LineWidth', 0.5, 'LineStyle', ':');
    end
end

sgtitle('Méta-Connectivité (MC) réordonnée par Méta-Modules (Réf: G1)', 'Color', 'w', 'FontSize', 14);