%% ========================================================================
%  FIGURE : META-HUBS (A) ET SENSIBILITÉ RÉGIONALE À L'ÂGE (B)
%% ========================================================================

% 1. Calcul de la Nodal Trimer Strength pour tous les sujets
% (Si nodal_tMC_all n'est pas déjà dans ton workspace)
N_nodes = 68;
N_subjects = 49;
nodal_tMC_all = zeros(N_subjects, N_nodes);

[row_idx, col_idx] = find(triu(true(N_nodes), 1));
edge_map = zeros(N_nodes, N_nodes);
for e = 1:length(row_idx)
    edge_map(row_idx(e), col_idx(e)) = e;
    edge_map(col_idx(e), row_idx(e)) = e;
end

fprintf('Calcul des scores régionaux (tMC) pour %d sujets...\n', N_subjects);
for s = 1:N_subjects
    SUB = eval(sprintf('SUBJECT_%d', s));
    MC_sub = dFCstream2MC(SUB.dFCstream); %
    
    for i = 1:N_nodes
        t_sum = 0; count = 0;
        for j = 1:N_nodes
            if j == i, continue; end
            for k = j+1:N_nodes
                if k == i, continue; end
                e1 = edge_map(i, j); e2 = edge_map(j, k); e3 = edge_map(i, k);
                t_sum = t_sum + (MC_sub(e1,e2) + MC_sub(e2,e3) + MC_sub(e1,e3))/3;
                count = count + 1;
            end
        end
        nodal_tMC_all(s, i) = t_sum / count;
    end
end

%% 2. STATISTIQUES ET PRÉPARATION DES GRAPHIQUES
% Moyenne globale pour identifier les Hubs
mean_nodal_tMC = mean(nodal_tMC_all, 1);
[sorted_hubs, idx_hubs] = sort(mean_nodal_tMC, 'ascend');

% Corrélations avec l'âge pour chaque ROI
r_age = zeros(N_nodes, 1);
p_age = zeros(N_nodes, 1);
for i = 1:N_nodes
    [r_age(i), p_age(i)] = corr(ages, nodal_tMC_all(:, i));
end
[sorted_r, idx_r] = sort(r_age, 'ascend');

%% 3. GÉNÉRATION DES FIGURES (Style Horizontal Bar)
figure('Name', 'Analyse Régionale des Trimères', 'Color', 'k', 'Units', 'normalized', 'Position', [0.1 0.1 0.8 0.8]);

% --- GRAPH A : Nodal Trimer Strength (Identification des Meta-hubs) ---
subplot(1, 2, 1);
b1 = barh(1:N_nodes, sorted_hubs, 'FaceColor', [0.4 0.4 0.4], 'EdgeColor', 'none');
hold on;
% Colorer les Top 10 Meta-hubs (en haut du graph car ascend)
for m = (N_nodes-9):N_nodes
    patch(get(b1,'XData'), get(b1,'YData'), [0.9 0.6 0.1], 'FaceAlpha', 1); % Orange/Or
end
set(gca, 'Color', 'k', 'XColor', 'w', 'YColor', 'w', 'FontSize', 7);
set(gca, 'YTick', 1:N_nodes, 'YTickLabel', labels_68(idx_hubs)); %
xlabel('Nodal Trimer Strength (tMC)');
title('A. Hiérarchie des Meta-hubs (Global)', 'Color', 'w', 'FontSize', 12);
grid on; set(gca, 'GridColor', [0.3 0.3 0.3]);

% --- GRAPH B : Effet de l'Âge (Corrélations r) ---
subplot(1, 2, 2);
b2 = barh(1:N_nodes, sorted_r, 'FaceColor', 'flat', 'EdgeColor', 'none');
% Colorer les régions significatives (p < 0.05) en rouge
for i = 1:N_nodes
    actual_roi_idx = idx_r(i);
    if p_age(actual_roi_idx) < 0.05
        b2.CData(i, :) = [0.8 0.2 0.2]; % Rouge
    else
        b2.CData(i, :) = [0.4 0.4 0.4]; % Gris
    end
end
set(gca, 'Color', 'k', 'XColor', 'w', 'YColor', 'w', 'FontSize', 7);
set(gca, 'YTick', 1:N_nodes, 'YTickLabel', labels_68(idx_r));
xlabel('Corrélation avec l''Âge (Pearson r)');
title('B. Sensibilité au Vieillissement (Rouge: p<0.05)', 'Color', 'w', 'FontSize', 12);
grid on; set(gca, 'GridColor', [0.3 0.3 0.3]);

sgtitle('Organisation Spatio-temporelle de Haut Niveau (Trimères)', 'Color', 'w', 'FontSize', 16);