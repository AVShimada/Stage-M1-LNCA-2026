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