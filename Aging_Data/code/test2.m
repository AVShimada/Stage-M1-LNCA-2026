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