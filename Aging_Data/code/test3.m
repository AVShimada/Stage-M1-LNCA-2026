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