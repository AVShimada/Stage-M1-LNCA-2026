% On s'assure que les stats sont prêtes
mean_nodal_tMC = mean(nodal_tMC_all, 1);
[sorted_hubs, idx_hubs] = sort(mean_nodal_tMC, 'ascend');

r_age = zeros(N_nodes, 1);
p_age = zeros(N_nodes, 1);
for i = 1:N_nodes
    [r_age(i), p_age(i)] = corr(ages, nodal_tMC_all(:, i));
end
[sorted_r, idx_r] = sort(r_age, 'ascend');

% --- CRÉATION DE LA FIGURE ---
figure('Name', 'Analyse Régionale des Trimères', 'Color', 'k', 'Units', 'normalized', 'Position', [0.1 0.1 0.8 0.8]);

% --- GRAPH A : Nodal Trimer Strength (Meta-hubs) ---
subplot(1, 2, 1);
% On utilise 'FaceColor', 'flat' pour permettre la coloration individuelle
b1 = barh(1:N_nodes, sorted_hubs, 'FaceColor', 'flat', 'EdgeColor', 'none');

% Initialisation en gris
b1.CData = repmat([0.4 0.4 0.4], N_nodes, 1); 

% Colorer les Top 10 Meta-hubs (les 10 dernières barres car trié 'ascend')
% On utilise du orange/doré comme dans Arbabyazd
for m = (N_nodes-9):N_nodes
    b1.CData(m, :) = [0.9 0.6 0.1]; 
end

set(gca, 'Color', 'k', 'XColor', 'w', 'YColor', 'w', 'FontSize', 7);
set(gca, 'YTick', 1:N_nodes, 'YTickLabel', labels_68(idx_hubs));
xlabel('Nodal Trimer Strength (tMC)');
title('A. Hiérarchie des Meta-hubs (Global)', 'Color', 'w', 'FontSize', 12);
grid on; set(gca, 'GridColor', [0.3 0.3 0.3]);

% --- GRAPH B : Effet de l'Âge (Corrélations r) ---
subplot(1, 2, 2);
b2 = barh(1:N_nodes, sorted_r, 'FaceColor', 'flat', 'EdgeColor', 'none');

% Colorer en rouge les régions où p < 0.05
b2.CData = repmat([0.4 0.4 0.4], N_nodes, 1); 
for i = 1:N_nodes
    actual_roi_idx = idx_r(i);
    if p_age(actual_roi_idx) < 0.05
        b2.CData(i, :) = [0.8 0.2 0.2]; 
    end
end

set(gca, 'Color', 'k', 'XColor', 'w', 'YColor', 'w', 'FontSize', 7);
set(gca, 'YTick', 1:N_nodes, 'YTickLabel', labels_68(idx_r));
xlabel('Corrélation avec l''Âge (Pearson r)');
title('B. Sensibilité au Vieillissement (Rouge: p<0.05)', 'Color', 'w', 'FontSize', 12);
grid on; set(gca, 'GridColor', [0.3 0.3 0.3]);

sgtitle('Organisation Spatio-temporelle de Haut Niveau (Trimères)', 'Color', 'w', 'FontSize', 16);